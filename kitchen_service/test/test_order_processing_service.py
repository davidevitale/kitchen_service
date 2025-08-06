# cartella: tests/service/test_order_processing_service.py

import unittest
from unittest.mock import Mock
from uuid import uuid4

from service.order_service import OrderProcessingService
from model.order import Order

class TestOrderProcessingService(unittest.TestCase):
    """Suite di test per l'orchestratore OrderProcessingService."""

    def setUp(self):
        self.kitchen_id = uuid4()
        # Mock per ogni servizio dipendente
        self.mock_availability_service = Mock()
        self.mock_menu_service = Mock()
        self.mock_status_service = Mock()
        self.mock_producer = Mock()

        # Istanza del servizio da testare con tutti i suoi mock
        self.service = OrderProcessingService(
            kitchen_id=self.kitchen_id,
            availability_service=self.mock_availability_service,
            menu_service=self.mock_menu_service,
            status_service=self.mock_status_service,
            producer=self.mock_producer
        )

    def test_handle_order_request_publishes_acceptance_when_all_available(self):
        """Verifica che venga pubblicata un'offerta se tutto è disponibile."""
        # ARRANGE
        order = Order(order_id=str(uuid4()), dish_id=str(uuid4()), kitchen_id="k1", customer_id="c1", delivery_address="a")
        self.mock_availability_service.is_available.return_value = True
        self.mock_menu_service.is_dish_available.return_value = True

        # ACT
        self.service.handle_order_request(order)

        # ASSERT
        self.mock_producer.publish_acceptance.assert_called_once()

    def test_handle_order_request_does_not_publish_if_kitchen_not_available(self):
        """Verifica che non venga pubblicata un'offerta se la cucina non è disponibile."""
        # ARRANGE
        order = Order(order_id=str(uuid4()), dish_id=str(uuid4()), kitchen_id="k1", customer_id="c1", delivery_address="a")
        self.mock_availability_service.is_available.return_value = False
        self.mock_menu_service.is_dish_available.return_value = True

        # ACT
        self.service.handle_order_request(order)

        # ASSERT
        self.mock_producer.publish_acceptance.assert_not_called()

    def test_handle_order_assignment_commits_dish_and_updates_status(self):
        """Verifica che, assegnato un ordine, venga decrementata la scorta e aggiornato lo stato."""
        # ARRANGE
        order_id = uuid4()
        dish_id = uuid4()
        # Simuliamo che il commit del piatto abbia successo
        self.mock_menu_service.commit_order_dish.return_value = True
        
        # ACT
        self.service.handle_order_assignment(order_id, dish_id, self.kitchen_id)

        # ASSERT
        # Verifica che i metodi corretti dei servizi dipendenti siano stati chiamati
        self.mock_menu_service.commit_order_dish.assert_called_once_with(dish_id)
        self.mock_availability_service.increment_load.assert_called_once()
        self.mock_status_service.update_status.assert_called_once_with(order_id, 'in_preparation')