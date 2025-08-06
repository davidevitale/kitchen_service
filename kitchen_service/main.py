# main.py (nella root del progetto)

import threading
import uvicorn
from api import app, get_order_processing_service, order_status_repo, kitchen_producer
from consumers.event_consumers import EventConsumer

# Riusiamo le istanze create nel modulo api per mantenere la coerenza
order_processing_service = get_order_processing_service()
consumer = EventConsumer(
    order_processing_service=order_processing_service,
    order_status_repo=order_status_repo,
    kitchen_producer=kitchen_producer
)

def run_api():
    """Avvia il server API FastAPI con Uvicorn."""
    print("AVVIO: Server API su porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def run_consumer():
    """Avvia il consumatore di eventi Kafka in un loop infinito."""
    print("AVVIO: Consumer Kafka...")
    consumer.listen()

if __name__ == "__main__":
    print("--- Avvio del Microservizio Cucina ---")
    
    # Eseguiamo API e Consumer in due thread separati per farli funzionare in parallelo.
    # In un ambiente di produzione, questi sarebbero processi o container separati.
    api_thread = threading.Thread(target=run_api, name="APIThread")
    consumer_thread = threading.Thread(target=run_consumer, name="ConsumerThread")
    
    api_thread.start()
    consumer_thread.start()
    
    api_thread.join()
    consumer_thread.join()