# cartella: producers/__init__.py

from .kafka_producers import producer
from .kitchen_producers import KitchenEventProducer

__all__ = [
    "producer",
    "KitchenEventProducer",
]