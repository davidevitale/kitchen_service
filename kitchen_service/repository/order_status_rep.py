import etcd3
from typing import Optional, Iterable, Tuple
from uuid import UUID
from model import OrderStatus

class OrderStatusRepository:
    def __init__(self, host='localhost', port=2379):
        self.etcd = etcd3.client(host=host, port=port)

    def _key(self, order_id: UUID) -> str:
        return f"order_status:{str(order_id)}"

    # --- FUNZIONI CRUD BASE ---

    def save_status(self, status: OrderStatus):
        """Salva o sovrascrive uno stato (non sicuro per la concorrenza)."""
        self.etcd.put(self._key(status.order_id), status.json())

    def get_status(self, order_id: UUID) -> Tuple[Optional[OrderStatus], Optional[int]]:
        """
        MODIFICATO: Recupera lo stato e la sua versione (mod_revision).
        Restituisce una tupla (OrderStatus, revision) o (None, None).
        """
        key = self._key(order_id)
        value, metadata = self.etcd.get(key)
        
        if not value or not metadata:
            return None, None
            
        status_obj = OrderStatus.parse_raw(value.decode())
        revision = metadata.mod_revision
        return status_obj, revision

    # --- FUNZIONI AVANZATE E ATOMICHE (CORRETTE PER IL REPOSITORY) ---

    def safe_update(self, new_status: OrderStatus, expected_revision: int) -> bool:
        """
        NUOVO: Esegue un aggiornamento sicuro basato sulla versione (mod_revision).
        Questa è un'operazione atomica di Compare-and-Swap (CAS).
        Restituisce True se l'aggiornamento ha successo, False altrimenti.
        """
        key = self._key(new_status.order_id)
        
        # La transazione etcd confronta la mod_revision prima di scrivere.
        # Il repository non sa e non gli importa quale sia lo stato 'atteso'.
        # Verifica solo che nessuno abbia modificato il dato nel frattempo.
        success, _ = self.etcd.transaction(
            compare=[
                self.etcd.transactions.mod(key) == expected_revision
            ],
            success=[
                self.etcd.transactions.put(key, new_status.json())
            ],
            failure=[]
        )
        return success

    def watch_status_changes(self, order_id: UUID) -> Iterable[OrderStatus]:
        """
        Ascolta i cambiamenti di stato per un ordine specifico.
        Questa funzione è già corretta per un repository.
        """
        key = self._key(order_id)
        events_iterator, cancel = self.etcd.watch(key)
        try:
            for event in events_iterator:
                if event.value:
                    yield OrderStatus.parse_raw(event.value.decode())
        finally:
            cancel()