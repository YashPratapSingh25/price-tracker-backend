import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async
from models.TrackedProductModel import TrackedProduct
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore_async.client()
_trackedProducts = db.collection("tracked_products")

def toFirestoreMap(product : TrackedProduct):
    return {
      "imageUrl" : product.imageUrl,
      "title" : product.title,
      "currentPrice" : product.currentPrice,
      "prevPrice" : product.prevPrice,
      "dateAdded" : datetime.fromisoformat(product.dateAdded),
      "productUrl" : product.productUrl,
      "currentUser" : product.currentUser,
      "site" : product.site
    }

async def add_product(product : TrackedProduct):
    doc = product.docId
    await _trackedProducts.document(doc).set(
        toFirestoreMap(product),
        merge=True
    )


async def delete_product(docId : str):
    await _trackedProducts.document(docId).delete()

async def is_product_tracked(docId : str) -> bool:
    docRef = await _trackedProducts.document(docId).get()
    return docRef.exists