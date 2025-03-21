from pydantic import BaseModel

class TrackedProduct(BaseModel):
    docId : str
    imageUrl : str
    title : str
    currentPrice : str
    prevPrice : str
    dateAdded : str
    lastUpdated : str
    productUrl : str
    currentUser : str
    site : str