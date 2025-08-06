# cartella: service/menu_service.py
from uuid import UUID
from repository import MenuRepository

class MenuService:
    def __init__(self, menu_repo: MenuRepository, kitchen_id: UUID):
        self.repo = menu_repo
        self.kitchen_id = kitchen_id

    def is_dish_available(self, dish_id: UUID) -> bool:
        """Controlla se un singolo piatto ha quantità disponibile."""
        dish = self.repo.get_dish(self.kitchen_id, dish_id)
        return dish and dish.available_quantity > 0

    def commit_order_dish(self, dish_id: UUID) -> bool:
        """
        Esegue un decremento atomico della scorta per un piatto.
        Restituisce True se l'operazione ha successo, False altrimenti.
        """
        # Chiama il metodo atomico del repository
        result_code = self.repo.atomic_decrement_availability(self.kitchen_id, dish_id)
        
        # Il service interpreta il risultato.
        # Un codice di ritorno >= 0 indica successo.
        if result_code >= 0:
            print(f"INFO: Scorta per piatto {dish_id} decrementata. Nuova quantità: {result_code}")
            return True
        else:
            print(f"ERROR: Fallito commit per piatto {dish_id}. Codice: {result_code}")
            return False