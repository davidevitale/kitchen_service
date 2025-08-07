# main.py (nella root del progetto)
import asyncio
import uvicorn
from api.api_main import app, order_processing_service, order_status_repo, kitchen_producer
from consumers.event_consumers import EventConsumer
from producers import stop_kafka_producer

async def main():
    consumer = EventConsumer(
        order_processing_service=order_processing_service,
        order_status_repo=order_status_repo,
        kitchen_producer=kitchen_producer
    )
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    api_task = asyncio.create_task(server.serve())
    consumer_task = asyncio.create_task(consumer.listen())

    await asyncio.gather(api_task, consumer_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n--- Spegnimento del Microservizio Cucina ---")
    finally:
        asyncio.run(stop_kafka_producer())