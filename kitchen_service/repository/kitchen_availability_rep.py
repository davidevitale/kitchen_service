# cartella: repository/kitchen_availability_rep.py
from typing import Optional
from model import KitchenAvailability
from threading import Lock # Importa Lock

class KitchenAvailabilityRepository:
    def __init__(self):
        self.store = {}
        self._lock = Lock() # Aggiungi un lock

    # ... save e get ...

    def update(self, kitchen_id: str, kitchen_operational: bool = None, current_load: int = None):
        with self._lock: # Usa il lock per rendere l'operazione sicura
            if kitchen_id in self.store:
                if kitchen_operational is not None:
                    self.store[kitchen_id].kitchen_operational = kitchen_operational
                if current_load is not None:
                    self.store[kitchen_id].current_load = current_load