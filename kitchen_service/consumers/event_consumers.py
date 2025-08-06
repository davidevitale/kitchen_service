# cartella: consumers/event_consumer.py
from kafka import KafkaConsumer
import json
from uuid import UUID
from model import Order
from service import OrderProcessingService, OrderStatusRepository # Importiamo i servizi/repo necessari
from producers import KitchenEventProducer

# In un'applicazione reale, questo valore verrebbe da un file di configurazione
KAFKA_BROKER_URL = 'localhost:9092'

class EventConsumer:
    def __init__(
        self,
        order_processing_service: OrderProcessingService,
        order_status_repo: OrderStatusRepository,
        kitchen_producer: KitchenEventProducer
    ):
        """
        Inizializza il consumatore con le dipendenze necessarie per processare gli eventi.
        """
        self.order_processing_service = order_processing_service
        self.order_status_repo = order_status_repo
        self.producer = kitchen_producer
        
        # Si iscrive a tutti i topic di input del Servizio Cucina
        self.consumer = KafkaConsumer(
            "disponibilità",
            "conferma_ordine",
            "status",
            bootstrap_servers=KAFKA_BROKER_URL,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='kitchen_service_group' # Importante per la scalabilità
        )

    def listen(self):
        """
        Avvia il loop infinito di ascolto dei messaggi.
        Questo è il cuore del microservizio.
        """
        print("CONSUMER: Servizio Cucina in ascolto su Kafka...")
        for message in self.consumer:
            topic = message.topic
            data = message.value
            print(f"CONSUMER: Messaggio ricevuto su topic '{topic}': {data}")

            if topic == "disponibilità":
                # Il Servizio Ordini chiede disponibilità. Deserializziamo
                # il messaggio nel nostro modello Pydantic `Order`.
                order = Order(**data)
                self.order_processing_service.handle_order_request(order)

            elif topic == "conferma_ordine":
                # Il Servizio Ordini ha assegnato un ordine.
                order_id = UUID(data['order_id'])
                assigned_kitchen_id = UUID(data['assigned_kitchen_id'])
                # La cucina si mette al lavoro, non deve rispondere.
                # L'aggiornamento di stato verrà pubblicato separatamente.
                self.order_processing_service.handle_order_assignment(
                    order_id=order_id,
                    dish_id=UUID(data['dish_id']), # Assumendo che venga passato anche il dish_id
                    assigned_kitchen_id=assigned_kitchen_id
                )

            elif topic == "status":
                # Il Servizio Ordini sta chiedendo lo stato attuale di un ordine.
                order_id = UUID(data['order_id'])
                # Leggiamo lo stato dal nostro repository etcd
                status_obj, _ = self.order_status_repo.get_status(order_id)
                if status_obj:
                    # E lo pubblichiamo sul topic di risposta
                    self.producer.publish_status_update(status_obj)