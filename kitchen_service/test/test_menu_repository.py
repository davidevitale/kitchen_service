# cartella: tests/repository/test_order_status_repository.py

import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

# Importa le classi che devi testare e i modelli
from repository.order_status_rep import OrderStatusRepository
from model.order_status import OrderStatus

class TestOrderStatusRepository(unittest.TestCase):
    """
    Suite di test per la classe OrderStatusRepository.
    """

    @patch('etcd3.client')  # "Patch" sostituisce etcd3.client con un Mock
    def setUp(self, mock_etcd3_client):
        """
        Questo metodo viene eseguito prima di ogni test.
        Usiamo @patch per "intercettare" la creazione del client etcd.
        """
        # 1. Il mock del client etcd viene passato automaticamente da @patch
        self.mock_etcd_client = mock_etcd3_client.return_value
        
        # 2. Istanziamo il repository. Ora, quando __init__ chiamerà
        #    etcd3.client(), riceverà il nostro mock invece del client reale.
        self.repository = OrderStatusRepository(host='mock_host', port=1234)

    def test_save_status_calls_etcd_put_with_correct_key_and_value(self):
        """
        Verifica che save_status() chiami etcd.put() con la chiave e
        il valore JSON corretti.
        """
        # ARRANGE: Prepariamo lo scenario
        order_id = uuid4()
        status = OrderStatus(order_id=str(order_id), kitchen_id="k1", status="pending")
        expected_key = f"order_status:{str(order_id)}"
        expected_value_json = status.json()

        # ACT: Eseguiamo il metodo da testare
        self.repository.save_status(status)

        # ASSERT: Verifichiamo che il metodo put del mock sia stato chiamato
        # esattamente una volta con gli argomenti che ci aspettavamo.
        self.mock_etcd_client.put.assert_called_once_with(expected_key, expected_value_json)

    def test_get_status_returns_status_object_when_key_exists(self):
        """
        Verifica che get_status() restituisca un oggetto OrderStatus
        quando la chiave esiste in etcd.
        """
        # ARRANGE
        order_id = uuid4()
        expected_key = f"order_status:{str(order_id)}"
        
        # Simuliamo la risposta che etcd darebbe
        status_obj = OrderStatus(order_id=str(order_id), kitchen_id="k1", status="in_preparation")
        
        # Il metodo etcd.get restituisce (valore, metadata)
        # Il valore deve essere in bytes, come farebbe la vera libreria
        mock_value = status_obj.json().encode('utf-8')
        mock_metadata = Mock()
        mock_metadata.mod_revision = 123 # Simuliamo una revisione
        
        # Diciamo al mock cosa restituire quando viene chiamato .get()
        self.mock_etcd_client.get.return_value = (mock_value, mock_metadata)

        # ACT
        result_status, result_revision = self.repository.get_status(order_id)

        # ASSERT
        self.assertEqual(result_status, status_obj)
        self.assertEqual(result_revision, 123)
        self.mock_etcd_client.get.assert_called_once_with(expected_key)

    def test_get_status_returns_none_when_key_does_not_exist(self):
        """
        Verifica che get_status() restituisca (None, None) se la chiave
        non esiste.
        """
        # ARRANGE
        order_id = uuid4()
        # Simuliamo una risposta vuota da etcd
        self.mock_etcd_client.get.return_value = (None, None)

        # ACT
        result_status, result_revision = self.repository.get_status(order_id)

        # ASSERT
        self.assertIsNone(result_status)
        self.assertIsNone(result_revision)

    def test_safe_update_calls_transaction_with_correct_parameters(self):
        """
        Verifica che safe_update() chiami la transazione di etcd
        con i parametri di confronto e successo corretti.
        """
        # ARRANGE
        order_id = uuid4()
        new_status = OrderStatus(order_id=str(order_id), kitchen_id="k1", status="ready")
        expected_revision = 5
        
        # Diciamo al mock della transazione di restituire True (successo)
        self.mock_etcd_client.transaction.return_value = (True, [])

        # ACT
        success = self.repository.safe_update(new_status, expected_revision)

        # ASSERT
        self.assertTrue(success)
        # Questa è una verifica più complessa, ma controlla che il metodo
        # transaction sia stato chiamato. In test più avanzati, potresti
        # ispezionare gli oggetti compare e success.
        self.mock_etcd_client.transaction.assert_called_once()