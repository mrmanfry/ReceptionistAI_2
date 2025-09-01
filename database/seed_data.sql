-- Dati di esempio per Receptionist AI
-- Inserisci questi dati dopo aver creato le tabelle

-- Ristorante 1: Trattoria da Mario
INSERT INTO ristoranti (nome_ristorante, numero_twilio, system_prompt, telefono_escalation, orari_apertura, indirizzo) VALUES (
    'Trattoria da Mario',
    '+39021111111', -- SOSTITUIRE con il tuo numero Twilio reale
    'Sei un assistente virtuale efficiente e cortese per la Trattoria da Mario. I loro orari sono dalle 19:00 alle 23:00, dal martedì alla domenica. Sono chiusi il lunedì. Parla in modo amichevole ma professionale. Se un cliente chiede di parlare con qualcuno, trasferiscilo al numero +393331111111.',
    '+393331111111',
    'Martedì - Domenica: 19:00 - 23:00 (Chiuso il Lunedì)',
    'Via Roma 123, Milano'
);

-- Ristorante 2: Pizzeria da Gino (per test)
INSERT INTO ristoranti (nome_ristorante, numero_twilio, system_prompt, telefono_escalation, orari_apertura, indirizzo) VALUES (
    'Pizzeria da Gino',
    '+39062222222', -- SOSTITUIRE con un altro numero Twilio che possiedi
    'Sei l''assistente virtuale della Pizzeria da Gino. Sei molto veloce e informale. Gli orari sono 7 giorni su 7, dalle 18:30 a mezzanotte. Ricorda ai clienti che fanno la migliore pizza della città. Se un cliente chiede di parlare con qualcuno, trasferiscilo al numero +393332222222.',
    '+393332222222',
    'Tutti i giorni: 18:30 - 00:00',
    'Via Napoli 456, Roma'
);

-- Ristorante 3: Ristorante Elegante (esempio aggiuntivo)
INSERT INTO ristoranti (nome_ristorante, numero_twilio, system_prompt, telefono_escalation, orari_apertura, indirizzo) VALUES (
    'Ristorante Elegante',
    '+39063333333', -- SOSTITUIRE con un altro numero Twilio
    'Sei l''assistente virtuale del Ristorante Elegante, un ristorante di alta cucina. Parla in modo formale ed elegante. Gli orari sono dal martedì al sabato, dalle 12:00 alle 14:30 per il pranzo e dalle 19:30 alle 23:00 per la cena. Domenica e lunedì sono chiusi. Se un cliente chiede di parlare con qualcuno, trasferiscilo al numero +393333333333.',
    '+393333333333',
    'Martedì - Sabato: 12:00-14:30 e 19:30-23:00 (Chiuso Domenica e Lunedì)',
    'Via Elegante 789, Firenze'
);

-- Verifica i dati inseriti
SELECT id, nome_ristorante, numero_twilio, LEFT(system_prompt, 50) || '...' as prompt_preview 
FROM ristoranti;
