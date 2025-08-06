from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Literal

class OrderStatus(BaseModel):
    order_id: str
    kitchen_id: str
    status: Literal['pending', 'accepted', 'in_preparation', 'ready', 'delivered']
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
