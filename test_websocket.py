#!/usr/bin/env python3
"""
Script di test per verificare il funzionamento del WebSocket server
"""
import asyncio
import websockets
import json
import logging
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket():
    """Test del WebSocket endpoint"""
    uri = "ws://localhost:8000/"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connesso al WebSocket server")
            
            # Simula l'evento "connected"
            connected_message = {
                "event": "connected",
                "streamSid": "test-stream-123"
            }
            await websocket.send(json.dumps(connected_message))
            logger.info(f"Evento 'connected' inviato: {connected_message}")
            
            # Aspetta un po'
            await asyncio.sleep(1)
            
            # Simula alcuni pacchetti audio (µ-law codificati in Base64)
            # Creiamo alcuni dati audio di test (silenzio con un po' di rumore)
            import random
            for i in range(3):
                # Genera dati audio µ-law di test (valori casuali)
                test_audio = bytes([random.randint(0, 255) for _ in range(160)])  # 20ms a 8kHz
                audio_message = {
                    "event": "media",
                    "streamSid": "test-stream-123",
                    "media": {
                        "payload": base64.b64encode(test_audio).decode('utf-8')
                    }
                }
                await websocket.send(json.dumps(audio_message))
                logger.info(f"Pacchetto audio {i+1} inviato: {len(test_audio)} bytes")
                await asyncio.sleep(0.5)
            
            # Simula l'evento "stop"
            stop_message = {
                "event": "stop",
                "streamSid": "test-stream-123"
            }
            await websocket.send(json.dumps(stop_message))
            logger.info(f"Evento 'stop' inviato: {stop_message}")
            
            # Aspetta un po' per vedere la risposta
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Errore durante il test: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
