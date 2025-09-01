#!/usr/bin/env python3
"""
Script per aggiornare i numeri di telefono nel database
con i numeri Twilio reali.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def update_phone_numbers():
    """Aggiorna i numeri di telefono nel database"""
    
    # Stringa di connessione al database
    DATABASE_URL = "postgresql://receptionist_user:ReceptionistUser2024!@34.55.74.67:5432/receptionist_db"
    
    try:
        # Connessione al database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connessione al database riuscita")
        
        # Aggiorna il numero della Trattoria da Mario
        await conn.execute("""
            UPDATE ristoranti 
            SET numero_twilio = $1 
            WHERE nome_ristorante = 'Trattoria da Mario'
        """, '+1 631 612 6108')
        
        print("✅ Numero aggiornato per Trattoria da Mario: +1 631 612 6108")
        
        # Verifica l'aggiornamento
        result = await conn.fetch("""
            SELECT nome_ristorante, numero_twilio 
            FROM ristoranti 
            ORDER BY id
        """)
        
        print("\n📋 Numeri attuali nel database:")
        for row in result:
            print(f"  • {row['nome_ristorante']}: {row['numero_twilio']}")
        
        await conn.close()
        print("\n✅ Aggiornamento completato con successo!")
        
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")

if __name__ == "__main__":
    asyncio.run(update_phone_numbers())
