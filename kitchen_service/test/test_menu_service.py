# cartella: tests/service/test_menu_service.py

import unittest
from unittest.mock import Mock
from uuid import uuid4

from service.menu_service import MenuService
from model.menu import Dish

class TestMenuService(unittest.TestCase):
    """Suite di test per il MenuService."""

    def setUp(self):
        self.mock_menu_repo = Mock()
        self.kitchen_id = uuid4()
        self.menu_service = MenuService(
            menu_repo=self.mock_menu_repo,
            kitchen_id=self.kitchen_id
        )

    def test_is_dish_available_returns_true_when_quantity_is_positive(self):
        dish_id = uuid4()
        fake_dish = Dish(id=dish_id, name="Test", price=10.0, available_quantity=5)
        self.mock_menu_repo.get_dish.return_value = fake_dish
        self.assertTrue(self.menu_service.is_dish_available(dish_id))

    def test_is_dish_available_returns_false_when_quantity_is_zero(self):
        dish_id = uuid4()
        fake_dish = Dish(id=dish_id, name="Test", price=10.0, available_quantity=0)
        self.mock_menu_repo.get_dish.return_value = fake_dish
        self.assertFalse(self.menu_service.is_dish_available(dish_id))

    def test_commit_order_dish_returns_true_on_successful_decrement(self):
        dish_id = uuid4()
        self.mock_menu_repo.atomic_decrement_availability.return_value = 4 # Successo
        self.assertTrue(self.menu_service.commit_order_dish(dish_id))
        self.mock_menu_repo.atomic_decrement_availability.assert_called_once()

    def test_commit_order_dish_returns_false_on_failed_decrement(self):
        dish_id = uuid4()
        self.mock_menu_repo.atomic_decrement_availability.return_value = -3 # Fallimento
        self.assertFalse(self.menu_service.commit_order_dish(dish_id))