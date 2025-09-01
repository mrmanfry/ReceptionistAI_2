# Receptionist AI - WebSocket Server

Questo è il server WebSocket di base per il servizio Receptionist AI su Google Cloud Run che accetta connessioni da Twilio.

## Struttura del Progetto

- `main.py` - Server WebSocket principale con FastAPI
- `requirements.txt` - Dipendenze Python
- `Dockerfile` - Configurazione Docker per Cloud Run
- `.dockerignore` - File da escludere dal build Docker

## Installazione Locale

1. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

2. Avvia il server localmente:
```bash
uvicorn main:app --reload
```

Il server sarà disponibile su `http://localhost:8000`

## Deployment su Google Cloud Run

1. Build dell'immagine Docker:
```bash
docker build -t receptionist-ai .
```

2. Deploy su Cloud Run:
```bash
gcloud run deploy receptionist-ai \
  --image receptionist-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## Endpoint WebSocket

- **URL**: `ws://your-cloud-run-url/`
- **Metodo**: WebSocket
- **Descrizione**: Endpoint principale che accetta connessioni WebSocket da Twilio

## Logging

Il server configura automaticamente il logging per mostrare:
- Connessioni accettate
- Messaggi ricevuti da Twilio
- Disconnessioni

I log saranno visibili nei log di Cloud Run o nel terminale durante l'esecuzione locale.

## Test del WebSocket

Per testare il WebSocket localmente:

1. Avvia il server:
```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. In un altro terminale, esegui il test:
```bash
python3 test_simple.py
```

Il test simulerà una connessione WebSocket da Twilio e invierà eventi di test inclusi pacchetti audio.

### Eventi Supportati

Il server ora gestisce i seguenti eventi da Twilio:
- **`connected`**: Inizio della connessione WebSocket
- **`media`**: Pacchetti audio (decodificati da Base64 e convertiti da µ-law a PCM)
- **`stop`**: Fine della chiamata

### Processamento Audio

- **Decodifica Base64**: I pacchetti audio vengono decodificati da Base64
- **Conversione µ-law → PCM**: L'audio telefonico viene convertito in formato PCM lineare
- **Buffering**: L'audio viene accumulato in un buffer per il processing successivo

## Passo 3: Integrazione OpenAI

Il server ora include funzionalità AI complete:

### 🧠 Funzionalità AI Implementate

#### **3A. Rilevamento Parlato (VAD)**
- **Voice Activity Detection**: Rileva quando l'utente inizia e finisce di parlare
- **Configurazione**: 30ms frame, aggressività 3, 8kHz sample rate
- **Logica**: 25 frame di silenzio (750ms) dopo il parlato attivano il processing

#### **3B. Trascrizione e Pensiero (STT + LLM)**
- **Speech-to-Text**: OpenAI Whisper per trascrivere l'audio
- **Large Language Model**: GPT-4o-mini per generare risposte intelligenti
- **Prompt Personalizzato**: Configurato per "Trattoria da Mario"

#### **3C. Sintesi Vocale (TTS)**
- **Text-to-Speech**: OpenAI TTS con voce "nova"
- **Conversione Audio**: PCM 24kHz → 8kHz → µ-law per Twilio
- **Risposta Automatica**: Invia audio di risposta a Twilio

### 🔧 Configurazione OpenAI

1. **Crea un file `.env`** nella root del progetto:
```bash
OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
```

2. **Testa l'integrazione**:
```bash
python3 test_openai_integration.py
```

### 📊 Flusso Completo

1. **Ascolto**: Server riceve audio da Twilio
2. **VAD**: Rileva fine del parlato dell'utente
3. **STT**: Trascrive audio in testo
4. **LLM**: Genera risposta intelligente
5. **TTS**: Converte risposta in audio
6. **Risposta**: Invia audio a Twilio

## Passo 4: Sistema Multi-Tenant SaaS

Il server ora supporta un sistema multi-tenant completo:

### 🏗️ Architettura Database

#### **Schema PostgreSQL**
- **`ristoranti`**: Tabella principale con informazioni per ogni ristorante
- **`chiamate_log`**: Log delle chiamate per analytics
- **`configurazioni`**: Configurazioni avanzate per ristorante

#### **Dati Multi-Tenant**
- **Trattoria da Mario**: Numero +39021111111
- **Pizzeria da Gino**: Numero +39062222222  
- **Ristorante Elegante**: Numero +39063333333

### 🔧 Configurazione Database

1. **Crea il database PostgreSQL**:
```sql
-- Esegui database/schema.sql per creare le tabelle
-- Esegui database/seed_data.sql per inserire i dati di esempio
```

2. **Configura la connessione** nel file `.env`:
```bash
DATABASE_URL="postgresql://user:password@host:port/database"
```

3. **Testa la connessione**:
```bash
python3 test_database.py
```

### 🌐 Sistema Multi-Tenant

#### **Identificazione Ristorante**
- **URL WebSocket**: `wss://your-domain/?numero_chiamato={{To}}`
- **Estrazione**: Il server estrae il numero chiamato dall'URL
- **Ricerca DB**: Cerca il ristorante corrispondente nel database
- **Prompt Dinamico**: Carica il system_prompt specifico del ristorante

#### **TwiML Multi-Tenant**
```xml
<Response>
    <Connect>
        <Stream url="wss://YOUR_CLOUD_RUN_URL/?numero_chiamato={{To}}" />
    </Connect>
</Response>
```

### 📊 Logging e Analytics

- **Log Chiamate**: Ogni chiamata viene registrata nel database
- **Statistiche**: Durata, status, ristorante
- **Performance**: Monitoraggio per ogni tenant

### 🧪 Test Multi-Tenant

```bash
# Test con diversi ristoranti
python3 test_multitenant.py

# Test database
python3 test_database.py
```
