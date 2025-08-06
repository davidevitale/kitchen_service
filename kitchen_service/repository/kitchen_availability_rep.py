from typing import Optional
from model import KitchenAvailability

class KitchenAvailabilityRepository:
    def __init__(self):
        self.store = {}

    # Create
    def save(self, kitchen_avail: KitchenAvailability):
        self.store[kitchen_avail.kitchen_id] = kitchen_avail

    # Read
    def get(self, kitchen_id: str) -> Optional[KitchenAvailability]:
        return self.store.get(kitchen_id)

    # Update (esempio aggiornamento load e stato operativo)
    def update(self, kitchen_id: str, kitchen_operational: bool = None, current_load: int = None):
        if kitchen_id in self.store:
            if kitchen_operational is not None:
                self.store[kitchen_id].kitchen_operational = kitchen_operational
            if current_load is not None:
                self.store[kitchen_id].current_load = current_load

