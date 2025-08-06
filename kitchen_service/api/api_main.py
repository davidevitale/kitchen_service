# cartella: api/main.py

from fastapi import FastAPI, Depends, HTTPException
from uuid import UUID
from pydantic import BaseModel

# Importiamo i nostri servizi e repository
from service import (
    KitchenAvailabilityService,
    MenuService,
    OrderStatusService,
    OrderProcessingService
)
from repository import (
    MenuRepository,
    OrderStatusRepository,
    KitchenAvailabilityRepository
)
from producers import KitchenEventProducer

# Importa il modello OrderStatus
from model import OrderStatus

# --- Blocco di Inizializzazione delle Dipendenze (Dependency Injection) ---
# In un'applicazione reale, questi valori verrebbero da un file di configurazione o variabili d'ambiente.

# ID UNIVOCO DI QUESTA ISTANZA DI CUCINA
# Sostituisci con un UUID generato una sola volta per la tua cucina
KITCHEN_ID = UUID("123e4567-e89b-12d3-a456-426614174000") 

# Configurazione dei database
REDIS_CLUSTER_NODES = [{"host": "localhost", "port": 7001}] # Esempio per Redis Cluster
ETCD_HOST = 'localhost'
ETCD_PORT = 2379

# 1. Istanziamo i Repository
# NOTA: Qui va usata la versione sicura e atomica di MenuRepository!
menu_repo = MenuRepository(redis_cluster_nodes=REDIS_CLUSTER_NODES)
order_status_repo = OrderStatusRepository(host=ETCD_HOST, port=ETCD_PORT)
kitchen_availability_repo = KitchenAvailabilityRepository()

# 2. Istanziamo il Producer
kitchen_producer = KitchenEventProducer(kitchen_id=KITCHEN_ID)

# 3. Istanziamo i Servizi, iniettando le dipendenze
kitchen_availability_service = KitchenAvailabilityService(
    kitchen_repo=kitchen_availability_repo, 
    kitchen_id=KITCHEN_ID
)
menu_service = MenuService(
    menu_repo=menu_repo, 
    kitchen_id=KITCHEN_ID
)
order_status_service = OrderStatusService(
    status_repo=order_status_repo,
    kitchen_id=KITCHEN_ID,
    producer=kitchen_producer
)
order_processing_service = OrderProcessingService(
    kitchen_id=KITCHEN_ID,
    availability_service=kitchen_availability_service,
    menu_service=menu_service,
    status_service=order_status_service,
    producer=kitchen_producer
)

# 4. Funzioni "provider" per FastAPI
# Queste funzioni permettono a FastAPI di passare le istanze dei servizi agli endpoint
def get_order_processing_service():
    return order_processing_service

def get_kitchen_availability_service():
    return kitchen_availability_service

# --- Fine Blocco Inizializzazione ---


app = FastAPI(
    title="Kitchen Service API",
    description="API per gestire le operazioni di una Ghost Kitchen."
)

# --- Definizione degli Endpoint ---

@app.post("/orders/{order_id}/ready", status_code=202)
def mark_order_as_ready(
    order_id: UUID,
    service: OrderProcessingService = Depends(get_order_processing_service)
):
    """
    Endpoint per un operatore per marcare un ordine come 'pronto per il ritiro'.
    Questa è la funzionalità chiave richiesta dalla traccia.
    """
    try:
        service.handle_order_ready(order_id)
        return {"message": "Stato ordine aggiornato a 'ready'. Notifica inviata."}
    except Exception as e:
        # In un'app reale, gestiresti eccezioni più specifiche
        raise HTTPException(status_code=500, detail=str(e))


class KitchenStatusUpdate(BaseModel):
    is_operational: bool

@app.put("/kitchen/status", status_code=200)
def set_kitchen_operational_status(
    status_update: KitchenStatusUpdate,
    service: KitchenAvailabilityService = Depends(get_kitchen_availability_service)
):
    """

    Endpoint per aprire o chiudere la cucina.
    """
    service.set_operational_status(status_update.is_operational)
    status_text = "operativa" if status_update.is_operational else "chiusa"
    return {"message": f"Stato della cucina impostato su: {status_text}"}


@app.get("/orders/{order_id}/status", response_model=OrderStatus)
def get_order_status(order_id: UUID):
    """
    Endpoint per interrogare lo stato attuale di un ordine.
    """
    status, _ = order_status_repo.get_status(order_id)
    if not status:
        raise HTTPException(status_code=404, detail="Stato ordine non trovato")
    return status