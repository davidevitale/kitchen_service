import redis
import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from model import Dish # Assumiamo che esista un modello Pydantic 'Dish'

class MenuRepository:
    """
    Repository per la gestione del menu della cucina.
    
    Questo repository è stato corretto per:
    1. Usare un client Redis standard (`redis.Redis`) per evitare errori di connessione
       con istanze Redis standalone.
    2. Utilizzare una struttura dati più efficiente e idiomatica per Redis:
       invece di un unico JSON, ogni piatto è un Hash separato.
    3. Sostituire complessi script Lua con comandi atomici nativi di Redis
       (come HINCRBY), che è più semplice, veloce e meno propenso a errori.
    """

    def __init__(self, redis_config: Dict[str, Any]):
        """
        Inizializza il repository e stabilisce la connessione a Redis.

        :param redis_config: Un dizionario con i parametri di connessione 
                             (es. {'host': 'localhost', 'port': 6379, 'db': 0}).
        """
        try:
            # Usiamo redis.Redis per connetterci a un'istanza standalone.
            self.redis = redis.Redis(**redis_config, decode_responses=True)
            self.redis.ping()
            print(f"Connessione a Redis ({redis_config.get('host')}:{redis_config.get('port')}) riuscita.")
        except redis.exceptions.ConnectionError as e:
            print(f"ERRORE: Impossibile connettersi a Redis. Dettagli: {e}")
            raise

    def _get_menu_key(self, kitchen_id: UUID) -> str:
        """Helper per generare la chiave Redis per il SET che contiene gli ID dei piatti di un menu."""
        return f"kitchen:{kitchen_id}:dishes"

    def _get_dish_key(self, dish_id: UUID) -> str:
        """Helper per generare la chiave Redis per l'Hash di un singolo piatto."""
        return f"dish:{dish_id}"

    def save_dish(self, kitchen_id: UUID, dish: Dish) -> None:
        """
        Salva un singolo piatto in Redis come Hash e aggiunge il suo ID al menu della cucina.
        
        :param kitchen_id: L'ID della cucina a cui appartiene il piatto.
        :param dish: L'oggetto Dish da salvare.
        """
        dish_key = self._get_dish_key(dish.id)
        menu_key = self._get_menu_key(kitchen_id)
        
        # Salva il piatto come un Hash. Usiamo .dict() se Dish è un modello Pydantic.
        self.redis.hset(dish_key, mapping=dish.dict())
        
        # Aggiunge l'ID del piatto al Set del menu della cucina per un recupero efficiente.
        self.redis.sadd(menu_key, str(dish.id))

    def get_dish(self, dish_id: UUID) -> Optional[Dish]:
        """
        Recupera un singolo piatto dal suo ID.

        :param dish_id: L'ID del piatto.
        :return: L'oggetto Dish o None se non trovato.
        """
        dish_key = self._get_dish_key(dish_id)
        dish_data = self.redis.hgetall(dish_key)
        
        if not dish_data:
            return None
        
        # Converte i valori recuperati (stringhe) nei tipi corretti per il modello Dish.
        # Questo è un esempio, potrebbe essere necessario adattarlo al tuo modello esatto.
        dish_data['id'] = UUID(dish_data['id'])
        dish_data['price'] = float(dish_data['price'])
        dish_data['available_quantity'] = int(dish_data['available_quantity'])
        
        return Dish(**dish_data)

    def get_all_dishes(self, kitchen_id: UUID) -> List[Dish]:
        """
        Recupera tutti i piatti per una data cucina.

        :param kitchen_id: L'ID della cucina.
        :return: Una lista di oggetti Dish.
        """
        menu_key = self._get_menu_key(kitchen_id)
        dish_ids = self.redis.smembers(menu_key)
        
        dishes = []
        for dish_id_str in dish_ids:
            dish = self.get_dish(UUID(dish_id_str))
            if dish:
                dishes.append(dish)
        return dishes

    # --- Metodi Atomici per Gestire la Disponibilità ---
    
    def atomic_set_availability(self, dish_id: UUID, new_quantity: int) -> int:
        """
        Imposta atomicamente la quantità di un piatto.
        Restituisce la nuova quantità.
        """
        dish_key = self._get_dish_key(dish_id)
        self.redis.hset(dish_key, 'available_quantity', new_quantity)
        return new_quantity

    def atomic_increment_availability(self, dish_id: UUID, amount: int = 1) -> int:
        """
        Incrementa atomicamente la quantità usando il comando nativo HINCRBY.
        Restituisce la nuova quantità.
        """
        dish_key = self._get_dish_key(dish_id)
        return self.redis.hincrby(dish_key, 'available_quantity', amount)

    def atomic_decrement_availability(self, dish_id: UUID, amount: int = 1) -> int:
        """
        Decrementa atomicamente la quantità. HINCRBY accetta anche valori negativi.
        Restituisce la nuova quantità.
        
        NOTA: Questo metodo non controlla se la quantità va sotto zero.
        La logica di business per prevenire quantità negative dovrebbe essere gestita
        nel service layer che chiama questo metodo.
        """
        dish_key = self._get_dish_key(dish_id)
        return self.redis.hincrby(dish_key, 'available_quantity', -amount)
