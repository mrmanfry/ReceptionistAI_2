#!/usr/bin/env python3
"""
Test semplice per verificare il server WebSocket
"""
import asyncio
import websockets
import json
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_test():
    """Test semplice del WebSocket"""
    uri = "ws://localhost:8000/"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connesso al WebSocket server")
            
            # Test 1: Evento connected
            connected_msg = {"event": "connected", "streamSid": "test-123"}
            await websocket.send(json.dumps(connected_msg))
            logger.info("✅ Evento 'connected' inviato")
            await asyncio.sleep(0.5)
            
            # Test 2: Un pacchetto audio
            test_audio = bytes([128] * 160)  # Audio di test (silenzio)
            audio_msg = {
                "event": "media",
                "streamSid": "test-123",
                "media": {"payload": base64.b64encode(test_audio).decode('utf-8')}
            }
            await websocket.send(json.dumps(audio_msg))
            logger.info("✅ Pacchetto audio inviato")
            await asyncio.sleep(0.5)
            
            # Test 3: Evento stop
            stop_msg = {"event": "stop", "streamSid": "test-123"}
            await websocket.send(json.dumps(stop_msg))
            logger.info("✅ Evento 'stop' inviato")
            await asyncio.sleep(0.5)
            
            logger.info("✅ Test completato con successo!")
            
    except Exception as e:
        logger.error(f"❌ Errore: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())
