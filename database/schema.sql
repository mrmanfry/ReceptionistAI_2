-- Schema del database per Receptionist AI
-- Database: receptionist_ai

-- Tabella principale per i ristoranti (multi-tenant)
CREATE TABLE ristoranti (
    id SERIAL PRIMARY KEY,
    nome_ristorante VARCHAR(255) NOT NULL,
    numero_twilio VARCHAR(50) UNIQUE NOT NULL, -- La chiave per identificare il ristorante
    system_prompt TEXT NOT NULL, -- Le istruzioni personalizzate per l'IA
    telefono_escalation VARCHAR(50), -- Numero per escalation umana
    orari_apertura TEXT, -- Orari di apertura in formato testo
    indirizzo TEXT, -- Indirizzo del ristorante
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per log delle chiamate (opzionale, per analytics)
CREATE TABLE chiamate_log (
    id SERIAL PRIMARY KEY,
    ristorante_id INTEGER REFERENCES ristoranti(id),
    stream_sid VARCHAR(100) NOT NULL,
    numero_chiamante VARCHAR(50),
    numero_chiamato VARCHAR(50),
    durata_chiamata INTEGER, -- in secondi
    timestamp_inizio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_fine TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'completed' -- completed, failed, escalated
);

-- Tabella per configurazioni avanzate (opzionale)
CREATE TABLE configurazioni (
    id SERIAL PRIMARY KEY,
    ristorante_id INTEGER REFERENCES ristoranti(id),
    chiave VARCHAR(100) NOT NULL,
    valore TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ristorante_id, chiave)
);

-- Indici per performance
CREATE INDEX idx_ristoranti_numero_twilio ON ristoranti(numero_twilio);
CREATE INDEX idx_chiamate_ristorante_id ON chiamate_log(ristorante_id);
CREATE INDEX idx_chiamate_timestamp ON chiamate_log(timestamp_inizio);

-- Trigger per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ristoranti_updated_at 
    BEFORE UPDATE ON ristoranti 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
