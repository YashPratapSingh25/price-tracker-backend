import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async
from models.TrackedProductModel import TrackedProduct
from google.cloud.firestore_v1.base_query import FieldFilter
import datetime
import asyncio

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore_async.client()
trackedProducts = db.collection("tracked_products")

def to_firestore_map(product : TrackedProduct):
    return {
      "imageUrl" : product.imageUrl,
      "title" : product.title,
      "currentPrice" : product.currentPrice,
      "prevPrice" : product.prevPrice,
      "dateAdded" : datetime.datetime.fromisoformat(product.dateAdded),
      "lastUpdated" : datetime.datetime.fromisoformat(product.dateAdded),
      "productUrl" : product.productUrl,
      "currentUser" : product.currentUser,
      "site" : product.site
    }

async def add_product(product : TrackedProduct):
    doc = product.docId
    await trackedProducts.document(doc).set(
        to_firestore_map(product),
        merge=True
    )
    await add_price_in_subcollection(docId=doc, current_price=product.currentPrice)
    

async def delete_product(docId : str):
    await trackedProducts.document(docId).delete()

async def is_product_tracked(docId : str) -> bool:
    docRef = await trackedProducts.document(docId).get()
    return docRef.exists


async def fetch_all_documents(userId : str):
    
    product_docs = []
    docs = trackedProducts.where(filter=FieldFilter("currentUser", "==", userId)).stream()

    async for doc in docs:
        product_docs.append(doc)
    return product_docs

async def update_price(docId : str, newPrice : str):
    doc = await trackedProducts.document(docId).get()
    doc_dict = doc.to_dict()
    prevPrice = doc_dict.get("currentPrice")
    await trackedProducts.document(docId).update({
        "currentPrice": newPrice,
        "prevPrice": prevPrice,
        "lastUpdated": firestore_async.SERVER_TIMESTAMP
    })
    await add_price_in_subcollection(docId=docId, current_price=newPrice)

async def add_price_in_subcollection(docId : str, current_price : str):
    today_str = str(datetime.date.today())
    await trackedProducts.document(docId).collection("priceHistory").document(today_str).set({
        "price" : current_price,
        "timestamp" : firestore_async.SERVER_TIMESTAMP
    })