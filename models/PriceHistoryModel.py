from pydantic import BaseModel
from datetime import date

class PriceHistory(BaseModel):
    date : date
    price : str