from typing import Optional, List
from model import Order

class OrderRepository:
    def __init__(self):
        self.store = {}

    # Create
    def save(self, order: Order):
        self.store[order.order_id] = order

    # Read
    def get(self, order_id: str) -> Optional[Order]:
        return self.store.get(order_id)

    # Update (sovrascrive tutto l'ordine)
    def update(self, order: Order):
        if order.order_id in self.store:
            self.store[order.order_id] = order

    # Delete
    def delete(self, order_id: str):
        if order_id in self.store:
            del self.store[order_id]

    # Lista tutti gli ordini (utile per debug o altri scopi)
    def list_all(self) -> List[Order]:
        return list(self.store.values())
