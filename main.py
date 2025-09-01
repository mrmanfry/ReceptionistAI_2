# main.py
import logging
import base64
import audioop
import io
import wave
import webrtcvad
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import AsyncOpenAI
from urllib.parse import parse_qs, urlparse
from config import OPENAI_API_KEY, VAD_AGGRESSIVENESS, VAD_FRAME_MS, VAD_SAMPLE_RATE, VAD_BYTES_PER_FRAME
from database.db_manager import db_manager

# --- Configurazione ---
logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Inizializza il client OpenAI solo se la chiave API è disponibile
client = None
if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logging.info("Client OpenAI inizializzato.")
else:
    logging.warning("OPENAI_API_KEY non configurata o non valida. Le funzionalità AI non saranno disponibili.")

# Variabili di stato della chiamata
is_speaking = False
speech_buffer = bytearray()
silence_frames = 0
audio_buffer = bytearray()
current_stream_sid = None
current_call_id = None
call_start_time = None

vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

# --- EVENT HANDLERS PER DATABASE ---
@app.on_event("startup")
async def startup():
    """Inizializza il database all'avvio dell'applicazione"""
    try:
        await db_manager.initialize()
        logging.info("Applicazione avviata e database inizializzato.")
    except Exception as e:
        logging.error(f"Errore durante l'inizializzazione del database: {e}")
        logging.warning("L'applicazione continuerà senza database. Le funzionalità multi-tenant non saranno disponibili.")

@app.on_event("shutdown")
async def shutdown():
    """Chiude le connessioni al database alla chiusura"""
    await db_manager.close()
    logging.info("Applicazione chiusa e connessioni database terminate.")

async def process_user_speech(websocket: WebSocket, stream_sid: str, numero_chiamato: str):
    """
    Funzione principale che gestisce la logica AI:
    1. Trascrive l'audio dell'utente
    2. Pensa a una risposta
    3. Converte la risposta in audio e la invia a Twilio
    """
    global audio_buffer
    logging.info("L'utente ha finito di parlare. Processo l'audio...")

    # Verifica se il client OpenAI è inizializzato
    if client is None:
        logging.error("Client OpenAI non inizializzato. Impossibile processare l'audio.")
        audio_buffer.clear()
        return

    try:
        # --- 1. TRASCRIVERE (Speech-to-Text) ---
        # Creiamo un file WAV in memoria per OpenAI
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # PCM 16-bit
            wf.setframerate(VAD_SAMPLE_RATE)
            wf.writeframes(audio_buffer)
        
        wav_buffer.seek(0)
        wav_buffer.name = "user_speech.wav" # Nome fittizio per l'API

        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=wav_buffer,
            response_format="text"
        )
        logging.info(f"Testo trascritto: '{transcript}'")

        # --- 2. PENSARE (LLM) ---
        # Recupera il prompt specifico per il ristorante dal database
        try:
            restaurant_info = await db_manager.get_restaurant_by_phone(numero_chiamato)
            
            if not restaurant_info:
                logging.warning(f"Ristorante non trovato per il numero: {numero_chiamato}")
                # Fallback a un prompt generico
                system_prompt = "Sei un assistente virtuale generico per ristoranti. Rispondi in modo cortese e conciso."
            else:
                system_prompt = restaurant_info['system_prompt']
                logging.info(f"Prompt caricato per {restaurant_info['nome_ristorante']} ({numero_chiamato})")
        except Exception as e:
            logging.error(f"Errore nel recupero delle informazioni del ristorante: {e}")
            # Fallback a un prompt generico
            system_prompt = "Sei un assistente virtuale generico per ristoranti. Rispondi in modo cortese e conciso."
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=0.7
        )
        ai_response_text = response.choices[0].message.content
        logging.info(f"Risposta AI (testo): '{ai_response_text}'")

        # --- 3. PARLARE (Text-to-Speech) ---
        speech_response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=ai_response_text,
            response_format="pcm" # Chiediamo PCM per una conversione più facile
        )
        
        # L'output di OpenAI TTS è PCM 24kHz. Dobbiamo ricampionarlo a 8kHz per Twilio.
        pcm_24k = speech_response.read()
        pcm_8k, _ = audioop.ratecv(pcm_24k, 2, 1, 24000, 8000, None)
        
        # E poi convertirlo in µ-law
        ulaw_response = audioop.lin2ulaw(pcm_8k, 2)
        
        # --- 4. RISPONDERE A TWILIO ---
        payload = base64.b64encode(ulaw_response).decode('utf-8')
        response_message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": payload
            }
        }
        await websocket.send_json(response_message)
        logging.info("Risposta audio inviata a Twilio.")

    except Exception as e:
        logging.error(f"Errore durante il processo AI: {e}")
    finally:
        # Pulisci il buffer per il prossimo turno di parola
        audio_buffer.clear()


@app.websocket("/{path:path}")
async def websocket_endpoint(websocket: WebSocket, path: str = ""):
    global is_speaking, speech_buffer, silence_frames, audio_buffer, current_stream_sid, current_call_id, call_start_time
    
    # --- NUOVO: ESTRAZIONE NUMERO CHIAMATO ---
    query_string = websocket.scope.get("query_string", b"").decode()
    
    # --- AGGIUNGI QUESTA RIGA ---
    logging.info(f"Query string ricevuta da Twilio: '{query_string}'")
    # ---------------------------
    
    parsed_query = parse_qs(query_string)
    numero_chiamato = parsed_query.get("numero_chiamato", [None])[0]
    
    await websocket.accept()
    
    if not numero_chiamato:
        logging.error("Numero chiamato non fornito nell'URL. Chiusura connessione.")
        await websocket.close()
        return
    
    logging.info(f"Connessione da Twilio per {numero_chiamato} accettata.")
    
    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")

            if event == "connected":
                current_stream_sid = message.get('streamSid')
                call_start_time = time.time()
                
                # Log dell'inizio chiamata nel database
                try:
                    restaurant_info = await db_manager.get_restaurant_by_phone(numero_chiamato)
                    if restaurant_info:
                        current_call_id = await db_manager.log_call_start(
                            restaurant_info['id'], 
                            current_stream_sid, 
                            message.get('start', {}).get('callSid', 'unknown'),
                            numero_chiamato
                        )
                        logging.info(f"Chiamata registrata nel database. ID: {current_call_id}")
                except Exception as e:
                    logging.error(f"Errore nel logging della chiamata: {e}")
                
                logging.info(f"Evento 'connected' ricevuto. Stream SID: {current_stream_sid}")
            
            elif event == "media":
                payload = message["media"]["payload"]
                chunk = base64.b64decode(payload)
                pcm_chunk = audioop.ulaw2lin(chunk, 2)
                
                audio_buffer.extend(pcm_chunk)

                # Logica VAD: processiamo l'audio in frame
                for i in range(0, len(pcm_chunk), VAD_BYTES_PER_FRAME):
                    frame = pcm_chunk[i:i+VAD_BYTES_PER_FRAME]
                    if len(frame) < VAD_BYTES_PER_FRAME:
                        continue
                    
                    if vad.is_speech(frame, VAD_SAMPLE_RATE):
                        is_speaking = True
                        silence_frames = 0
                    else:
                        if is_speaking:
                            silence_frames += 1

                    # Se rileva 25 frame di silenzio (circa 750ms) dopo aver parlato,
                    # l'utente ha finito il suo turno.
                    if not is_speaking and len(audio_buffer) > 0:
                        continue # Ignora il silenzio iniziale
                    
                    if is_speaking and silence_frames > 25:
                        is_speaking = False
                        silence_frames = 0
                        await process_user_speech(websocket, current_stream_sid, numero_chiamato)

            elif event == "stop":
                logging.info(f"Chiamata terminata: {message.get('streamSid')}")
                
                # Log della fine chiamata nel database
                if current_call_id and call_start_time:
                    try:
                        durata_secondi = int(time.time() - call_start_time)
                        await db_manager.log_call_end(current_call_id, durata_secondi, 'completed')
                        logging.info(f"Chiamata registrata nel database. Durata: {durata_secondi} secondi")
                    except Exception as e:
                        logging.error(f"Errore nel logging della fine chiamata: {e}")
                
                # Reset dello stato
                audio_buffer.clear()
                is_speaking = False
                silence_frames = 0
                current_stream_sid = None
                current_call_id = None
                call_start_time = None
                break
    
    except WebSocketDisconnect:
        logging.warning("Connessione da Twilio chiusa.")
        
        # Log della fine chiamata nel database (se non già fatto)
        if current_call_id and call_start_time:
            try:
                durata_secondi = int(time.time() - call_start_time)
                await db_manager.log_call_end(current_call_id, durata_secondi, 'disconnected')
                logging.info(f"Chiamata registrata nel database (disconnessa). Durata: {durata_secondi} secondi")
            except Exception as e:
                logging.error(f"Errore nel logging della disconnessione: {e}")
        
        # Reset dello stato
        audio_buffer.clear()
        is_speaking = False
        silence_frames = 0
        current_stream_sid = None
        current_call_id = None
        call_start_time = None
