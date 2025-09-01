#!/usr/bin/env python3
"""
Gestore del database per Receptionist AI
"""
import asyncpg
import logging
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv("DATABASE_URL")
        
    async def initialize(self):
        """Inizializza il pool di connessioni al database"""
        if not self.database_url:
            raise ValueError("DATABASE_URL non configurata nelle variabili d'ambiente")
        
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=10
        )
        logging.info("Pool di connessioni al database creato.")
        
        # Crea le tabelle se non esistono
        await self._create_tables_if_not_exist()
        
    async def _create_tables_if_not_exist(self):
        """Crea le tabelle del database se non esistono"""
        try:
            async with self.pool.acquire() as connection:
                # Verifica se la tabella ristoranti esiste
                table_exists = await connection.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'ristoranti'
                    );
                    """
                )
                
                if not table_exists:
                    logging.info("Creazione tabelle del database...")
                    
                    # Crea le tabelle
                    await connection.execute("""
                        CREATE TABLE ristoranti (
                            id SERIAL PRIMARY KEY,
                            nome_ristorante VARCHAR(255) NOT NULL,
                            numero_twilio VARCHAR(50) UNIQUE NOT NULL,
                            system_prompt TEXT NOT NULL,
                            telefono_escalation VARCHAR(50),
                            orari_apertura TEXT,
                            indirizzo TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    
                    await connection.execute("""
                        CREATE TABLE chiamate_log (
                            id SERIAL PRIMARY KEY,
                            ristorante_id INTEGER REFERENCES ristoranti(id),
                            stream_sid VARCHAR(100) NOT NULL,
                            numero_chiamante VARCHAR(50),
                            numero_chiamato VARCHAR(50),
                            durata_chiamata INTEGER,
                            timestamp_inizio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            timestamp_fine TIMESTAMP WITH TIME ZONE,
                            status VARCHAR(20) DEFAULT 'completed'
                        );
                    """)
                    
                    await connection.execute("""
                        CREATE TABLE configurazioni (
                            id SERIAL PRIMARY KEY,
                            ristorante_id INTEGER REFERENCES ristoranti(id),
                            chiave VARCHAR(100) NOT NULL,
                            valore TEXT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(ristorante_id, chiave)
                        );
                    """)
                    
                    # Crea indici
                    await connection.execute("CREATE INDEX idx_ristoranti_numero_twilio ON ristoranti(numero_twilio);")
                    await connection.execute("CREATE INDEX idx_chiamate_ristorante_id ON chiamate_log(ristorante_id);")
                    await connection.execute("CREATE INDEX idx_chiamate_timestamp ON chiamate_log(timestamp_inizio);")
                    
                    # Crea trigger per updated_at
                    await connection.execute("""
                        CREATE OR REPLACE FUNCTION update_updated_at_column()
                        RETURNS TRIGGER AS $$
                        BEGIN
                            NEW.updated_at = CURRENT_TIMESTAMP;
                            RETURN NEW;
                        END;
                        $$ language 'plpgsql';
                    """)
                    
                    await connection.execute("""
                        CREATE TRIGGER update_ristoranti_updated_at 
                            BEFORE UPDATE ON ristoranti 
                            FOR EACH ROW 
                            EXECUTE FUNCTION update_updated_at_column();
                    """)
                    
                    # Inserisci dati di esempio
                    await connection.execute("""
                        INSERT INTO ristoranti (nome_ristorante, numero_twilio, system_prompt, telefono_escalation, orari_apertura, indirizzo)
                        VALUES 
                        ('Trattoria da Mario', '+39021111111', 'Sei un assistente virtuale per la Trattoria da Mario. Rispondi in modo cortese e conciso. Orari: 19:00-23:00, chiuso lunedì.', '+393331111111', '19:00-23:00, chiuso lunedì', 'Via Roma 123, Milano'),
                        ('Pizzeria da Gino', '+39062222222', 'Sei l''assistente virtuale della Pizzeria da Gino. Sei veloce e informale. Orari: 7 giorni su 7, 18:30-24:00.', '+393332222222', '18:30-24:00, tutti i giorni', 'Via Napoli 456, Roma')
                        ON CONFLICT (numero_twilio) DO NOTHING;
                    """)
                    
                    logging.info("Tabelle del database create con successo.")
                else:
                    logging.info("Tabelle del database già esistenti.")
                    
        except Exception as e:
            logging.error(f"Errore durante la creazione delle tabelle: {e}")
            # Non bloccare l'avvio dell'applicazione se le tabelle non possono essere create
        
    async def close(self):
        """Chiude il pool di connessioni"""
        if self.pool:
            await self.pool.close()
            logging.info("Pool di connessioni al database chiuso.")
            
    async def get_restaurant_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Recupera le informazioni di un ristorante dal numero di telefono"""
        if not self.pool:
            raise RuntimeError("Database non inizializzato")
            
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, nome_ristorante, numero_twilio, system_prompt, 
                       telefono_escalation, orari_apertura, indirizzo
                FROM ristoranti 
                WHERE numero_twilio = $1
                """,
                phone_number
            )
            
            if row:
                return dict(row)
            return None
            
    async def log_call_start(self, ristorante_id: int, stream_sid: str, 
                           numero_chiamante: str, numero_chiamato: str) -> int:
        """Registra l'inizio di una chiamata"""
        if not self.pool:
            raise RuntimeError("Database non inizializzato")
            
        async with self.pool.acquire() as connection:
            call_id = await connection.fetchval(
                """
                INSERT INTO chiamate_log 
                (ristorante_id, stream_sid, numero_chiamante, numero_chiamato)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                ristorante_id, stream_sid, numero_chiamante, numero_chiamato
            )
            return call_id
            
    async def log_call_end(self, call_id: int, durata_secondi: int, status: str = 'completed'):
        """Registra la fine di una chiamata"""
        if not self.pool:
            raise RuntimeError("Database non inizializzato")
            
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE chiamate_log 
                SET durata_chiamata = $1, timestamp_fine = CURRENT_TIMESTAMP, status = $2
                WHERE id = $3
                """,
                durata_secondi, status, call_id
            )
            
    async def get_restaurant_stats(self, ristorante_id: int, giorni: int = 30) -> Dict[str, Any]:
        """Recupera statistiche per un ristorante"""
        if not self.pool:
            raise RuntimeError("Database non inizializzato")
            
        async with self.pool.acquire() as connection:
            stats = await connection.fetchrow(
                """
                SELECT 
                    COUNT(*) as totale_chiamate,
                    AVG(durata_chiamata) as durata_media,
                    COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalation
                FROM chiamate_log 
                WHERE ristorante_id = $1 
                AND timestamp_inizio >= CURRENT_TIMESTAMP - INTERVAL '$2 days'
                """,
                ristorante_id, giorni
            )
            
            return dict(stats) if stats else {
                'totale_chiamate': 0,
                'durata_media': 0,
                'escalation': 0
            }

# Istanza globale del database manager
db_manager = DatabaseManager()
