#!/usr/bin/env python3
"""
Script per aggiornare i numeri di telefono nel database Google Cloud SQL
con i numeri Twilio reali.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def update_cloud_database():
    """Aggiorna i numeri di telefono nel database Google Cloud SQL"""
    
    # Stringa di connessione al database Google Cloud SQL
    DATABASE_URL = "postgresql://receptionist_user:ReceptionistUser2024!@34.55.74.67:5432/receptionist_db"
    
    try:
        print("🔗 Connessione al database Google Cloud SQL...")
        
        # Connessione al database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connessione al database riuscita")
        
        # Prima mostriamo i dati attuali
        print("\n📋 Dati attuali nel database:")
        current_data = await conn.fetch("""
            SELECT id, nome_ristorante, numero_twilio 
            FROM ristoranti 
            ORDER BY id
        """)
        
        for row in current_data:
            print(f"  • ID {row['id']}: {row['nome_ristorante']} - {row['numero_twilio']}")
        
        # Aggiorna il numero della Trattoria da Mario
        print(f"\n🔄 Aggiornamento numero per Trattoria da Mario...")
        await conn.execute("""
            UPDATE ristoranti 
            SET numero_twilio = $1 
            WHERE nome_ristorante = 'Trattoria da Mario'
        """, '+1 631 612 6108')
        
        print("✅ Numero aggiornato per Trattoria da Mario: +1 631 612 6108")
        
        # Verifica l'aggiornamento
        print("\n📋 Dati aggiornati nel database:")
        updated_data = await conn.fetch("""
            SELECT id, nome_ristorante, numero_twilio 
            FROM ristoranti 
            ORDER BY id
        """)
        
        for row in updated_data:
            print(f"  • ID {row['id']}: {row['nome_ristorante']} - {row['numero_twilio']}")
        
        await conn.close()
        print("\n✅ Aggiornamento completato con successo!")
        print("\n🎯 Prossimi passi:")
        print("  1. Configura il TwiML Bin su Twilio")
        print("  2. Collega il numero +1 631 612 6108 al webhook")
        print("  3. Fai una chiamata di test!")
        
    except Exception as e:
        print(f"❌ Errore durante l'aggiornamento: {e}")
        print(f"   Dettagli: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(update_cloud_database())
