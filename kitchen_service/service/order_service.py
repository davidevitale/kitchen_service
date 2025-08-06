# cartella: service/order_processing_service.py

from uuid import UUID
from model import Order
from .kitchen_service import KitchenAvailabilityService
from .menu_service import MenuService
from .order_service import OrderStatusService
# from producers import KitchenEventProducer

class OrderProcessingService:
    def __init__(
        self,
        kitchen_id: UUID,
        availability_service: KitchenAvailabilityService,
        menu_service: MenuService,
        status_service: OrderStatusService,
        # producer: KitchenEventProducer
    ):
        self.kitchen_id = kitchen_id
        self.availability_service = availability_service
        self.menu_service = menu_service
        self.status_service = status_service
        # self.producer = producer

    def handle_order_request(self, order: Order):
        """
        Orchestra la verifica di disponibilità completa.
        """
        # Usa gli altri servizi per prendere decisioni
        is_kitchen_avail = self.availability_service.is_available()
        is_dish_avail = self.menu_service.is_dish_available(UUID(order.dish_id))

        if is_kitchen_avail and is_dish_avail:
            # La cucina è disponibile, pubblica la sua offerta
            # self.producer.publish_acceptance_offer(order.order_id)
            print(f"INFO: Cucina {self.kitchen_id} disponibile per ordine {order.order_id}, offerta inviata.")
        else:
            print(f"INFO: Cucina {self.kitchen_id} non disponibile per ordine {order.order_id}.")


    def handle_order_assignment(self, order_id: UUID, dish_id: UUID, assigned_kitchen_id: UUID):
        """
        Orchestra l'accettazione e l'inizio della preparazione di un ordine.
        """
        if self.kitchen_id != assigned_kitchen_id:
            return # Ordine non per noi

        print(f"INFO: Ordine {order_id} assegnato a questa cucina.")
        
        # 1. Tenta di committare il piatto (decremento scorta)
        commit_success = self.menu_service.commit_order_dish(dish_id)
        
        if not commit_success:
            print(f"ERROR: Fallito il commit del piatto {dish_id} per l'ordine {order_id}! Scorta esaurita all'ultimo secondo.")
            # In un sistema reale, qui andrebbe pubblicato un evento di fallimento
            return

        # 2. Se il commit riesce, incrementa il carico e aggiorna lo stato
        self.availability_service.increment_load()
        self.status_service.update_status(order_id, 'in_preparation')

    def handle_order_ready(self, order_id: UUID):
        """Orchestra il completamento di un ordine."""
        self.availability_service.decrement_load()
        self.status_service.update_status(order_id, 'ready')