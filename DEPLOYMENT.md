# Deployment Guide - Receptionist AI

## Prerequisiti

1. **Account Google Cloud** con billing attivato
2. **Google Cloud CLI** installato e configurato
3. **Chiave API OpenAI** valida
4. **Docker** installato (opzionale, per build locale)

## Configurazione Iniziale

### 1. Configura Google Cloud CLI
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Configura la Chiave API OpenAI
Crea un file `.env` nella root del progetto:
```bash
OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
```

## Deployment su Google Cloud Run

### Opzione 1: Deployment Automatico (Raccomandato)

1. **Push del codice su GitHub** (se non già fatto)
2. **Connetti Cloud Build a GitHub**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

### Opzione 2: Deployment Manuale

1. **Build dell'immagine Docker**:
   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/receptionist-ai .
   ```

2. **Push dell'immagine**:
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/receptionist-ai
   ```

3. **Deploy su Cloud Run**:
   ```bash
   gcloud run deploy receptionist-ai \
     --image gcr.io/YOUR_PROJECT_ID/receptionist-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 512Mi \
     --cpu 1 \
     --max-instances 10
   ```

## Configurazione Twilio

### 1. Crea un Media Stream
Nel tuo TwiML, aggiungi:
```xml
<Response>
    <Connect>
        <Stream url="wss://YOUR_CLOUD_RUN_URL/" />
    </Connect>
</Response>
```

### 2. Configura il Webhook
- **URL**: `https://YOUR_CLOUD_RUN_URL/`
- **Metodo**: WebSocket
- **Eventi**: `connected`, `media`, `stop`

## Variabili d'Ambiente

### Cloud Run Environment Variables
```bash
gcloud run services update receptionist-ai \
  --set-env-vars OPENAI_API_KEY="sk-your-actual-key"
```

### Oppure tramite Console Web
1. Vai su Cloud Run Console
2. Seleziona il servizio `receptionist-ai`
3. Vai su "Edit & Deploy New Revision"
4. Sezione "Variables & Secrets"
5. Aggiungi `OPENAI_API_KEY`

## Monitoraggio e Logs

### Visualizza Logs
```bash
gcloud logs tail --service=receptionist-ai
```

### Metriche Cloud Run
- **CPU Usage**: Monitora l'utilizzo CPU
- **Memory Usage**: Monitora l'utilizzo memoria
- **Request Count**: Numero di richieste
- **Request Latency**: Latenza delle richieste

## Troubleshooting

### Problemi Comuni

1. **Errore 500 - OpenAI API Key**:
   - Verifica che la chiave API sia configurata correttamente
   - Controlla i logs per errori di autenticazione

2. **Timeout WebSocket**:
   - Aumenta il timeout di Cloud Run
   - Verifica la connessione Twilio

3. **Errore VAD**:
   - Controlla che webrtcvad sia installato correttamente
   - Verifica la configurazione audio

### Debug Locale
```bash
# Test locale
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test WebSocket
python3 test_simple.py

# Test OpenAI (richiede chiave API valida)
python3 test_openai_integration.py
```

## Scaling e Performance

### Configurazioni Raccomandate
- **Memory**: 512Mi (minimo), 1Gi (raccomandato)
- **CPU**: 1 vCPU
- **Max Instances**: 10-50 (dipende dal traffico)
- **Concurrency**: 80 (default)

### Ottimizzazioni
1. **Caching**: Implementa cache per risposte comuni
2. **Connection Pooling**: Riutilizza connessioni OpenAI
3. **Async Processing**: Usa background tasks per operazioni lunghe

## Sicurezza

### Best Practices
1. **Rotazione Chiavi API**: Cambia regolarmente la chiave OpenAI
2. **Secrets Management**: Usa Google Secret Manager per le chiavi
3. **Network Security**: Configura VPC se necessario
4. **Rate Limiting**: Implementa rate limiting per prevenire abusi

### Secret Manager (Raccomandato)
```bash
# Crea il secret
echo -n "sk-your-actual-key" | gcloud secrets create openai-api-key --data-file=-

# Aggiorna il servizio
gcloud run services update receptionist-ai \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

## Costi Stimati

### Cloud Run
- **CPU**: ~$0.00002400 per vCPU-secondo
- **Memory**: ~$0.00000250 per GB-secondo
- **Requests**: $0.40 per milione di richieste

### OpenAI
- **Whisper**: $0.006 per minuto
- **GPT-4o-mini**: $0.00015 per 1K tokens
- **TTS**: $0.015 per 1K caratteri

### Stima Mensile (1000 chiamate)
- **Cloud Run**: ~$10-20
- **Openai**: ~$50-100
- **Totale**: ~$60-120/mese
