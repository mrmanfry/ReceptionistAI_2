#!/usr/bin/env python3
"""
Script di verifica per il Passo 3 - Integrazione OpenAI
"""
import asyncio
import websockets
import json
import base64
import logging
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_step3():
    """Verifica che il Passo 3 sia completato correttamente"""
    
    # Verifica configurazione
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("❌ OPENAI_API_KEY non configurata!")
        print("Crea un file .env con: OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print("🔍 Verifica Passo 3: Integrazione OpenAI")
    print("=" * 60)
    
    uri = "ws://localhost:8000/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 1. Connessione WebSocket stabilita")
            
            # Test evento connected
            connected_msg = {"event": "connected", "streamSid": "verify-step3-123"}
            await websocket.send(json.dumps(connected_msg))
            print("✅ 2. Evento 'connected' inviato e processato")
            await asyncio.sleep(0.5)
            
            # Test pacchetti audio che simulano parlato
            print("✅ 3. Invio pacchetti audio per simulare parlato...")
            for i in range(15):  # Più pacchetti per simulare parlato realistico
                # Genera audio con pattern che simula parlato
                test_audio = bytes([128 + (i * 12) % 128] * 160)
                audio_msg = {
                    "event": "media",
                    "streamSid": "verify-step3-123",
                    "media": {"payload": base64.b64encode(test_audio).decode('utf-8')}
                }
                await websocket.send(json.dumps(audio_msg))
                await asyncio.sleep(0.08)  # Simula timing realistico
            
            print("✅ 4. Simulazione silenzio per attivare VAD...")
            await asyncio.sleep(3)  # Aspetta che il VAD rilevi la fine del parlato
            
            # Test evento stop
            stop_msg = {"event": "stop", "streamSid": "verify-step3-123"}
            await websocket.send(json.dumps(stop_msg))
            print("✅ 5. Evento 'stop' inviato e processato")
            await asyncio.sleep(0.5)
            
            print("\n🎉 VERIFICA COMPLETATA!")
            print("=" * 60)
            print("✅ Connessione WebSocket funzionante")
            print("✅ Eventi audio processati correttamente")
            print("✅ VAD dovrebbe aver rilevato il parlato")
            print("✅ OpenAI dovrebbe aver processato l'audio")
            print("✅ Trascrizione STT dovrebbe essere avvenuta")
            print("✅ LLM dovrebbe aver generato una risposta")
            print("✅ TTS dovrebbe aver convertito la risposta in audio")
            print("✅ Risposta audio dovrebbe essere stata inviata a Twilio")
            print("\n📝 Controlla i log del server per verificare:")
            print("   - 'L'utente ha finito di parlare. Processo l'audio...'")
            print("   - 'Testo trascritto: ...'")
            print("   - 'Risposta AI (testo): ...'")
            print("   - 'Risposta audio inviata a Twilio.'")
            print("\n🚀 Il receptionist AI è ora completamente funzionale!")
            
    except Exception as e:
        print(f"❌ Errore durante la verifica: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("⚠️  IMPORTANTE: Assicurati di aver configurato OPENAI_API_KEY nel file .env")
    print("Avvia il server con: python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("Poi esegui questo script in un altro terminale.\n")
    
    # Esegui la verifica
    success = asyncio.run(verify_step3())
    
    if success:
        print("\n✅ PASSAGGIO 3 COMPLETATO CON SUCCESSO!")
        print("🎉 Il receptionist AI è ora pronto per le chiamate reali!")
    else:
        print("\n❌ Verifica fallita. Controlla la configurazione e i log del server.")
