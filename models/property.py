from typing import Optional
from pydantic import BaseModel, Field
import uuid

class PropertySchema(BaseModel):
    property_id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Generate UUID by default
    title: str = "Untitled"  # Default title if missing
    price: Optional[float] = Field(default=None, ge=0)  # Price must be >= 0
    price_per_meter: Optional[float] = None
    area: Optional[float] = None
    street: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    affiliation: Optional[str] = None
    typeApt: Optional[str] = None
    rooms: Optional[str] = None
    url: str = "https://example.com"
    website: str = "default.com" 
    typeOfSale: Optional[str] = None
    owner_id: int = 1

