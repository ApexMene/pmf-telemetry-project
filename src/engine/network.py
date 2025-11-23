"""
NOTA PERSONALE POST-TEST:
Durante il test scritto non sono riuscito a rispondere alla domanda
sulle differenze tra TCP e UDP (applicato alla telemetria live). 
Ho deciso di approfondire l'argomento e implementare questo simulatore per dimostrare di aver colmato la lacuna.

APPLICATA AL MOTORSPORT:

1. TCP (Transmission Control Protocol):
   - Caratteristiche: Handshake, controllo errori, riordino pacchetti. Lento ma affidabile.
   - Uso MotoStudent: È la scelta OBBLIGATORIA per lo scarico dati ai box (Reg. B.10.3).
     Non possiamo permetterci di perdere neanche un millisecondo di log.

2. UDP (User Datagram Protocol):
   - Caratteristiche: Fire-and-forget, bassa latenza, nessuna garanzia di arrivo.
   - Uso Motorsport: Ideale per live streaming video o telemetria real-time (dove permesso, visto che nel regolamento è vietato),
     dove la velocità è prioritaria rispetto all'integrità del singolo pacchetto.



La funzione 'simulate_transfer' dimostra la differenza pratica:
l'UDP è veloce ma introduce perdita dati -> Packet Loss, mentre il TCP garantisce l'integrità.

"""


import time
import random
import polars as pl


def simulate_transfer(df, protocol, progress_bar, status_txt):
    total_chunks = 100
    chunk_size = df.height // total_chunks
    received = []
    
    # configurazine protocollo
    # meglio "in" che verificare uguale per robustezza
    if "TCP" in protocol:
        delay, loss_prob = 0.02, 0.0
    else: # UDP
        delay, loss_prob = 0.003, 0.2
        
    for i in range(total_chunks):
        time.sleep(delay)
        progress_bar.progress(i+1)
        status_txt.text(f"Trasmesso pacchetto {i+1}/{total_chunks} via {protocol}...")
        
        if random.random() > loss_prob:
            start = i * chunk_size
            
            # se ultimo giro, prendo fino alla fine
            if i == total_chunks - 1:
                chunk = df.slice(start, df.height - start) # prende il resto
            else:
                chunk = df.slice(start, chunk_size)
                
            received.append(chunk)
            
    if not received:
        return None, 0
    
    final_df = pl.concat(received)
    integrity = (final_df.height / df.height) * 100
    return final_df, integrity