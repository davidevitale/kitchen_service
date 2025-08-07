# cartella: producers/kitchen_producers.py
from .kafka_producers import get_kafka_producer
from model import OrderStatus
from uuid import UUID

class KitchenEventProducer:
    def __init__(self, kitchen_id: UUID):
            self.kitchen_id = kitchen_id
            
    async def publish_acceptance(self, order_id: UUID, kitchen_id: UUID):
        producer = await get_kafka_producer()
        topic = "kitchen.acceptance.responses"
        message = {"order_id": str(order_id), "kitchen_id": str(kitchen_id), "response": "AVAILABLE"}
        await producer.send_and_wait(topic, value=message)
        print(f"PRODUCER (async): Inviato a '{topic}': {message}")

    async def publish_status_update(self, status: OrderStatus):
        producer = await get_kafka_producer()
        topic = "order.status.updates"
        message = status.dict()
        await producer.send_and_wait(topic, value=message)
        print(f"PRODUCER (async): Inviato a '{topic}': {message}")