import redis
from typing import Optional
from uuid import UUID
from model import Dish, Menu

class MenuRepository:
    def __init__(self, redis_cluster_nodes):
        self.redis = redis.RedisCluster(startup_nodes=redis_cluster_nodes, decode_responses=True)

    def _menu_key(self, kitchen_id: UUID) -> str:
        return f"menu:{str(kitchen_id)}"

    # Create / Update (salva tutto il menu)
    def save_menu(self, menu: Menu):
        items_serialized = {str(dish_id): dish.json() for dish_id, dish in menu.items.items()}
        self.redis.delete(self._menu_key(menu.kitchen_id))  # elimina vecchio menu
        if items_serialized:
            self.redis.hset(self._menu_key(menu.kitchen_id), mapping=items_serialized)

    # Read
    def get_menu(self, kitchen_id: UUID) -> Optional[Menu]:
        items = self.redis.hgetall(self._menu_key(kitchen_id))
        if not items:
            return None
        dishes = {UUID(did): Dish.parse_raw(dish_json) for did, dish_json in items.items()}
        return Menu(kitchen_id=kitchen_id, items=dishes)

    # Update a singolo dish nel menu
    def update_dish(self, kitchen_id: UUID, dish: Dish):
        key = self._menu_key(kitchen_id)
        self.redis.hset(key, str(dish.id), dish.json())

    # Delete a singolo dish dal menu
    def delete_dish(self, kitchen_id: UUID, dish_id: UUID):
        self.redis.hdel(self._menu_key(kitchen_id), str(dish_id))

    # Delete tutto il menu
    def delete_menu(self, kitchen_id: UUID):
        self.redis.delete(self._menu_key(kitchen_id))
