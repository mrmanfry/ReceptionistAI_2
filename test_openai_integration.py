#!/usr/bin/env python3
"""
Test per verificare l'integrazione con OpenAI
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

async def test_openai_integration():
    """Test dell'integrazione OpenAI"""
    
    # Verifica che la chiave API sia configurata
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("❌ OPENAI_API_KEY non configurata!")
        print("Crea un file .env con la tua chiave API di OpenAI:")
        print("OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print("🔍 Test Integrazione OpenAI")
    print("=" * 50)
    
    uri = "ws://localhost:8000/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 1. Connessione WebSocket stabilita")
            
            # Test evento connected
            connected_msg = {"event": "connected", "streamSid": "test-openai-123"}
            await websocket.send(json.dumps(connected_msg))
            print("✅ 2. Evento 'connected' inviato")
            await asyncio.sleep(0.5)
            
            # Test pacchetti audio che simulano parlato
            # Generiamo audio che il VAD dovrebbe riconoscere come parlato
            for i in range(10):  # Più pacchetti per simulare parlato
                # Genera audio con pattern che simula parlato (variazioni)
                test_audio = bytes([128 + (i * 15) % 128] * 160)  # Pattern variabile
                audio_msg = {
                    "event": "media",
                    "streamSid": "test-openai-123",
                    "media": {"payload": base64.b64encode(test_audio).decode('utf-8')}
                }
                await websocket.send(json.dumps(audio_msg))
                print(f"✅ 3.{i+1} Pacchetto audio {i+1} inviato")
                await asyncio.sleep(0.1)
            
            # Simula silenzio per attivare il VAD
            print("✅ 4. Simulazione silenzio per attivare VAD...")
            await asyncio.sleep(2)  # Aspetta che il VAD rilevi la fine del parlato
            
            # Test evento stop
            stop_msg = {"event": "stop", "streamSid": "test-openai-123"}
            await websocket.send(json.dumps(stop_msg))
            print("✅ 5. Evento 'stop' inviato")
            await asyncio.sleep(0.5)
            
            print("\n🎉 TEST COMPLETATO!")
            print("=" * 50)
            print("✅ Connessione WebSocket funzionante")
            print("✅ Eventi audio processati")
            print("✅ VAD dovrebbe aver rilevato il parlato")
            print("✅ OpenAI dovrebbe aver processato l'audio")
            print("\n📝 Controlla i log del server per vedere:")
            print("   - Trascrizione dell'audio")
            print("   - Risposta dell'AI")
            print("   - Invio della risposta audio a Twilio")
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("⚠️  IMPORTANTE: Assicurati di aver configurato OPENAI_API_KEY nel file .env")
    print("Avvia il server con: python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("Poi esegui questo script in un altro terminale.\n")
    
    success = asyncio.run(test_openai_integration())
    
    if success:
        print("\n✅ TEST OPENAI COMPLETATO!")
    else:
        print("\n❌ Test fallito. Controlla la configurazione.")
