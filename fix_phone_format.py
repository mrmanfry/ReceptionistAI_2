#!/usr/bin/env python3
"""
Script per correggere il formato dei numeri di telefono
rimuovendo gli spazi per evitare problemi di parsing.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_phone_format():
    """Corregge il formato dei numeri di telefono rimuovendo gli spazi"""
    
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
            print(f"  • ID {row['id']}: {row['nome_ristorante']} - '{row['numero_twilio']}'")
        
        # Aggiorna il numero della Trattoria da Mario rimuovendo gli spazi
        print(f"\n🔄 Correzione formato numero per Trattoria da Mario...")
        await conn.execute("""
            UPDATE ristoranti 
            SET numero_twilio = $1 
            WHERE nome_ristorante = 'Trattoria da Mario'
        """, '+16316126108')  # Senza spazi
        
        print("✅ Numero corretto per Trattoria da Mario: +16316126108")
        
        # Verifica l'aggiornamento
        print("\n📋 Dati corretti nel database:")
        updated_data = await conn.fetch("""
            SELECT id, nome_ristorante, numero_twilio 
            FROM ristoranti 
            ORDER BY id
        """)
        
        for row in updated_data:
            print(f"  • ID {row['id']}: {row['nome_ristorante']} - '{row['numero_twilio']}'")
        
        await conn.close()
        print("\n✅ Formato numeri corretto con successo!")
        print("\n💡 Vantaggi del formato senza spazi:")
        print("  • Nessun problema di parsing")
        print("  • Confronti più affidabili")
        print("  • Compatibilità con tutti i sistemi")
        
    except Exception as e:
        print(f"❌ Errore durante la correzione: {e}")
        print(f"   Dettagli: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(fix_phone_format())
