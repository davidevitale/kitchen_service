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
        Tenta di "committare" un piatto per un ordine, decrementandone la scorta.
        Restituisce True se l'operazione ha successo, False altrimenti.
        
        ⚠️ AVVERTIMENTO SULLA SICUREZZA:
        Questo metodo presume che il metodo del repository sottostante
        (decrement_dish_availability) sia ATOMICO. Se non lo è, questo
        servizio non sarà affidabile.
        """
        # Questo è il punto in cui la versione non-atomica fallirebbe
        # sotto carico. Assumiamo che il repository sia sicuro.
        result = self.repo.decrement_dish_availability(self.kitchen_id, dish_id)
        
        # Un risultato non nullo o positivo indica successo
        return result is not None