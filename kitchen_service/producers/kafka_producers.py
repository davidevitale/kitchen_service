# cartella: producers/kafka_producer.py
from kafka import KafkaProducer
import json

# In un'applicazione reale, questo valore verrebbe da un file di configurazione
KAFKA_BROKER_URL = 'localhost:9092'

# Creiamo un'istanza singola del producer che verrà usata in tutta l'applicazione.
# Si connette ai broker Kafka e converte automaticamente i messaggi in JSON.
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
)