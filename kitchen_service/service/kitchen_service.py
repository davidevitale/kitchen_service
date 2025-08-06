# cartella: service/kitchen_availability_service.py
from uuid import UUID
from repository import KitchenAvailabilityRepository

# In una configurazione reale, questo sarebbe un valore esterno
MAX_CONCURRENT_ORDERS = 20 

class KitchenAvailabilityService:
    def __init__(self, kitchen_repo: KitchenAvailabilityRepository, kitchen_id: UUID):
        self.repo = kitchen_repo
        self.kitchen_id = kitchen_id

    def is_available(self) -> bool:
        """
        Controlla se la cucina è operativa e non ha raggiunto il carico massimo.
        """
        avail = self.repo.get(self.kitchen_id)
        if not avail:
            return False
        
        is_operational = avail.kitchen_operational
        is_not_overloaded = avail.current_load < MAX_CONCURRENT_ORDERS
        
        return is_operational and is_not_overloaded

    def increment_load(self):
        """Incrementa il carico di lavoro di 1 (quando un ordine viene accettato)."""
        avail = self.repo.get(self.kitchen_id)
        if avail:
            new_load = avail.current_load + 1
            self.repo.update(self.kitchen_id, current_load=new_load)

    def decrement_load(self):
        """Decrementa il carico di lavoro di 1 (quando un ordine è pronto)."""
        avail = self.repo.get(self.kitchen_id)
        if avail and avail.current_load > 0:
            new_load = avail.current_load - 1
            self.repo.update(self.kitchen_id, current_load=new_load)