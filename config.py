import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurazione VAD (Voice Activity Detection)
VAD_AGGRESSIVENESS = 3  # Da 0 (meno aggressivo) a 3 (più aggressivo)
VAD_FRAME_MS = 30
VAD_SAMPLE_RATE = 8000  # La telefonia usa 8000Hz
VAD_BYTES_PER_FRAME = int(VAD_SAMPLE_RATE * (VAD_FRAME_MS / 1000.0) * 2)

# Configurazione sistema
DEFAULT_SYSTEM_PROMPT = """Sei un assistente virtuale generico per ristoranti. 
Rispondi in modo cortese e conciso. Sei specializzato in:
- Prenotazioni di tavoli
- Informazioni sul menu
- Orari di apertura
- Indirizzo e contatti
- Specialità del giorno

Rispondi sempre in italiano in modo professionale ma amichevole."""
