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
