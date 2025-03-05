from pydantic import BaseModel

class LinkProduct(BaseModel):
    productUrl : str
    currentUser : str