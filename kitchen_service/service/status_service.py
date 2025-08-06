# cartella: service/order_status_service.py

from uuid import UUID
from repository import OrderStatusRepository
from model import OrderStatus
# from producers import KitchenEventProducer # Da importare nell'app reale

class OrderStatusService:
    def __init__(self, status_repo: OrderStatusRepository, kitchen_id: UUID): #, producer: KitchenEventProducer):
        self.repo = status_repo
        self.kitchen_id = kitchen_id
        # self.producer = producer

    def update_status(self, order_id: UUID, new_status_literal: str) -> bool:
        """
        Aggiorna lo stato di un ordine in modo sicuro e pubblica l'evento.
        Restituisce True se l'aggiornamento riesce, altrimenti False.
        """
        # 1. Legge lo stato attuale e la sua versione per un aggiornamento sicuro
        _, revision = self.repo.get_status(order_id)

        # Prepara il nuovo oggetto di stato
        new_status = OrderStatus(
            order_id=order_id,
            kitchen_id=self.kitchen_id,
            status=new_status_literal
        )

        success = False
        if revision is None:
            # Lo stato non esiste, è il primo. Lo salviamo direttamente.
            self.repo.save_status(new_status)
            success = True
        else:
            # Lo stato esiste, eseguiamo un aggiornamento sicuro
            success = self.repo.safe_update(new_status, expected_revision=revision)

        # 4. Se l'aggiornamento riesce, pubblica l'evento
        if success:
            # self.producer.publish_status_update(new_status)
            print(f"INFO: Stato ordine {order_id} aggiornato a '{new_status_literal}' e pubblicato.")
        else:
            print(f"WARN: Conflitto di versione per ordine {order_id}. Aggiornamento fallito.")
        
        return success