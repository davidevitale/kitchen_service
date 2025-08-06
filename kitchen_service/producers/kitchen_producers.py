# cartella: producers/kitchen_event_producer.py

from .kafka_producer import producer
from model import OrderStatus
from uuid import UUID

class KitchenEventProducer:
    def publish_acceptance(self, order_id: UUID, kitchen_id: UUID):
        """
        Pubblica sul topic 'accettazione' per comunicare la propria disponibilità.
        """
        topic = "accettazione"
        message = {
            "order_id": str(order_id),
            "kitchen_id": str(kitchen_id),
            "response": "AVAILABLE"
        }
        print(f"PRODUCER: Inviando al topic '{topic}': {message}")
        producer.send(topic, value=message)
        producer.flush() # Assicura l'invio immediato

    def publish_status_update(self, status: OrderStatus):
        """
        Pubblica lo stato attuale di un ordine sul topic 'status_update'.
        """
        topic = "status_update"
        # Usiamo .dict() di Pydantic per convertire l'oggetto in un dizionario
        message = status.dict()
        print(f"PRODUCER: Inviando al topic '{topic}': {message}")
        producer.send(topic, value=message)
        producer.flush()