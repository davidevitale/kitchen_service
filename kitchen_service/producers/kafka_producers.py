# cartella: producers/kafka_producers.py
from aiokafka import AIOKafkaProducer
import json
import asyncio

KAFKA_BROKER_URL = 'localhost:9092'
_producer_instance = None

async def get_kafka_producer():
    """Crea e avvia un producer singleton quando viene richiesto per la prima volta."""
    global _producer_instance
    if _producer_instance is None:
        loop = asyncio.get_event_loop()
        _producer_instance = AIOKafkaProducer(
            loop=loop,
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        await _producer_instance.start()
    return _producer_instance

async def stop_kafka_producer():
    """Ferma il producer in modo pulito alla chiusura dell'app."""
    global _producer_instance
    if _producer_instance:
        await _producer_instance.stop()