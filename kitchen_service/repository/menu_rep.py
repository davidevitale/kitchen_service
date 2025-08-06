# cartella: repository/menu_rep.py
import redis
from typing import Optional, List
from uuid import UUID
from model import Dish, Menu

# Script Lua per operazioni atomiche. Questa è best practice.
SET_QUANTITY_SCRIPT = """
local dish_json = redis.call('HGET', KEYS[1], ARGV[1])
if not dish_json then return -1 end
local quantity_pattern = '"available_quantity":%s*%d+'
if not string.match(dish_json, quantity_pattern) then return -2 end
local new_quantity = tonumber(ARGV[2])
local new_dish_json = string.gsub(dish_json, quantity_pattern, '"available_quantity":'..tostring(new_quantity))
redis.call('HSET', KEYS[1], ARGV[1], new_dish_json)
return new_quantity
"""

INCREMENT_QUANTITY_SCRIPT = """
local amount = tonumber(ARGV[2])
local dish_json = redis.call('HGET', KEYS[1], ARGV[1])
if not dish_json then return -1 end
local quantity_str = string.match(dish_json, '"available_quantity":%s*(%d+)')
if not quantity_str then return -2 end
local new_quantity = tonumber(quantity_str) + amount
local new_dish_json = string.gsub(dish_json, '"available_quantity":%s*'..quantity_str, '"available_quantity":'..tostring(new_quantity))
redis.call('HSET', KEYS[1], ARGV[1], new_dish_json)
return new_quantity
"""

DECREMENT_QUANTITY_SCRIPT = """
local amount = tonumber(ARGV[2])
local dish_json = redis.call('HGET', KEYS[1], ARGV[1])
if not dish_json then return -1 end
local quantity_str = string.match(dish_json, '"available_quantity":%s*(%d+)')
if not quantity_str then return -2 end
local quantity = tonumber(quantity_str)
if quantity < amount then return -3 end -- Non abbastanza quantità
local new_quantity = quantity - amount
local new_dish_json = string.gsub(dish_json, '"available_quantity":%s*'..quantity_str, '"available_quantity":'..tostring(new_quantity))
redis.call('HSET', KEYS[1], ARGV[1], new_dish_json)
return new_quantity
"""

class MenuRepository:
    def __init__(self, redis_cluster_nodes: List[dict]):
        self.redis = redis.RedisCluster(startup_nodes=redis_cluster_nodes, decode_responses=True)
        # Registra gli script per efficienza
        self.set_script = self.redis.register_script(SET_QUANTITY_SCRIPT)
        self.increment_script = self.redis.register_script(INCREMENT_QUANTITY_SCRIPT)
        self.decrement_script = self.redis.register_script(DECREMENT_QUANTITY_SCRIPT)

    # ... metodi get/save/update/delete invariati ...

    def get_dish(self, kitchen_id: UUID, dish_id: UUID) -> Optional[Dish]:
        dish_json = self.redis.hget(self._menu_key(kitchen_id), str(dish_id))
        return Dish.parse_raw(dish_json) if dish_json else None

    # --- Metodi Atomici per Gestire la Disponibilità ---

    def atomic_set_availability(self, kitchen_id: UUID, dish_id: UUID, new_quantity: int) -> int:
        """Imposta atomicamente la quantità. Restituisce la nuova quantità o un codice di errore."""
        key = self._menu_key(kitchen_id)
        return int(self.set_script(keys=[key], args=[str(dish_id), new_quantity]))

    def atomic_increment_availability(self, kitchen_id: UUID, dish_id: UUID, amount: int = 1) -> int:
        """Incrementa atomicamente la quantità. Restituisce la nuova quantità o un codice di errore."""
        key = self._menu_key(kitchen_id)
        return int(self.increment_script(keys=[key], args=[str(dish_id), amount]))

    def atomic_decrement_availability(self, kitchen_id: UUID, dish_id: UUID, amount: int = 1) -> int:
        """Decrementa atomicamente la quantità. Restituisce la nuova quantità o un codice di errore."""
        key = self._menu_key(kitchen_id)
        return int(self.decrement_script(keys=[key], args=[str(dish_id), amount]))