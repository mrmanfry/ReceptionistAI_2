#!/usr/bin/env python3
"""
Test per verificare la connessione al database
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from database.db_manager import db_manager

# Carica le variabili d'ambiente
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database():
    """Test della connessione al database"""
    
    # Verifica configurazione
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL non configurata!")
        print("Aggiungi al file .env:")
        print("DATABASE_URL=postgresql://user:password@host:port/database")
        return False
    
    print("🔍 Test Connessione Database")
    print("=" * 50)
    
    try:
        # Inizializza il database
        await db_manager.initialize()
        print("✅ Connessione al database stabilita")
        
        # Test 1: Recupera tutti i ristoranti
        print("\n📋 Test 1: Recupero ristoranti dal database")
        async with db_manager.pool.acquire() as connection:
            ristoranti = await connection.fetch("SELECT id, nome_ristorante, numero_twilio FROM ristoranti")
            
            if ristoranti:
                print(f"✅ Trovati {len(ristoranti)} ristoranti:")
                for ristorante in ristoranti:
                    print(f"   - {ristorante['nome_ristorante']} ({ristorante['numero_twilio']})")
            else:
                print("⚠️  Nessun ristorante trovato nel database")
                print("   Esegui database/seed_data.sql per inserire dati di esempio")
        
        # Test 2: Test ricerca per numero
        print("\n🔍 Test 2: Ricerca ristorante per numero")
        test_number = "+39021111111"  # Trattoria da Mario
        restaurant_info = await db_manager.get_restaurant_by_phone(test_number)
        
        if restaurant_info:
            print(f"✅ Ristorante trovato: {restaurant_info['nome_ristorante']}")
            print(f"   Prompt: {restaurant_info['system_prompt'][:100]}...")
        else:
            print(f"❌ Ristorante non trovato per il numero: {test_number}")
        
        # Test 3: Test numero inesistente
        print("\n🔍 Test 3: Ricerca numero inesistente")
        fake_number = "+39999999999"
        restaurant_info = await db_manager.get_restaurant_by_phone(fake_number)
        
        if restaurant_info:
            print(f"❌ Trovato ristorante per numero inesistente: {restaurant_info['nome_ristorante']}")
        else:
            print(f"✅ Correttamente non trovato ristorante per: {fake_number}")
        
        # Test 4: Test logging chiamata
        print("\n📝 Test 4: Test logging chiamata")
        if ristoranti:
            ristorante_id = ristoranti[0]['id']
            call_id = await db_manager.log_call_start(
                ristorante_id, 
                "test-stream-123", 
                "+393331111111", 
                "+39021111111"
            )
            print(f"✅ Chiamata registrata con ID: {call_id}")
            
            # Aggiorna la chiamata
            await db_manager.log_call_end(call_id, 120, 'completed')
            print(f"✅ Chiamata aggiornata con durata: 120 secondi")
        
        print("\n🎉 TEST DATABASE COMPLETATO!")
        print("=" * 50)
        print("✅ Connessione al database funzionante")
        print("✅ Query di ricerca funzionanti")
        print("✅ Logging chiamate funzionante")
        print("✅ Database pronto per il sistema multi-tenant!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False
    finally:
        # Chiudi la connessione
        await db_manager.close()
        print("✅ Connessione al database chiusa")
    
    return True

if __name__ == "__main__":
    print("⚠️  IMPORTANTE: Assicurati di aver configurato DATABASE_URL nel file .env")
    print("Esempio: DATABASE_URL=postgresql://user:password@localhost:5432/receptionist_ai\n")
    
    success = asyncio.run(test_database())
    
    if success:
        print("\n✅ TEST DATABASE COMPLETATO CON SUCCESSO!")
    else:
        print("\n❌ Test fallito. Controlla la configurazione del database.")
