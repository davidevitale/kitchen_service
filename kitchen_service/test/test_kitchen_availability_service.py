# cartella: tests/service/test_kitchen_availability_service.py

import unittest
from unittest.mock import Mock
from uuid import uuid4

from service.kitchen_service import KitchenAvailabilityService
from model.kitchen_availability import KitchenAvailability

class TestKitchenAvailabilityService(unittest.TestCase):
    """Suite di test per il KitchenAvailabilityService."""

    def setUp(self):
        self.mock_kitchen_repo = Mock()
        self.kitchen_id = uuid4()
        self.service = KitchenAvailabilityService(
            kitchen_repo=self.mock_kitchen_repo,
            kitchen_id=self.kitchen_id
        )

    def test_is_available_returns_true_when_operational_and_not_overloaded(self):
        fake_availability = KitchenAvailability(
            kitchen_id=str(self.kitchen_id),
            kitchen_operational=True,
            current_load=5
        )
        self.mock_kitchen_repo.get.return_value = fake_availability
        self.assertTrue(self.service.is_available())

    def test_is_available_returns_false_when_not_operational(self):
        fake_availability = KitchenAvailability(
            kitchen_id=str(self.kitchen_id),
            kitchen_operational=False,
            current_load=5
        )
        self.mock_kitchen_repo.get.return_value = fake_availability
        self.assertFalse(self.service.is_available())