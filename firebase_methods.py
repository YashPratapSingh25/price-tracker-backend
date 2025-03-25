import firebase_admin
from firebase_admin import credentials, messaging
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
      "dateAdded" : firestore_async.SERVER_TIMESTAMP,
      "lastUpdated" : firestore_async.SERVER_TIMESTAMP,
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
    await delete_subcollection(docId)

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
    dict = doc.to_dict()
    title = dict.get("title")
    currentPrice : str = dict.get("currentPrice")
    await trackedProducts.document(docId).update({
        "currentPrice": newPrice,
        "lastUpdated": firestore_async.SERVER_TIMESTAMP
    })
    
    if float(currentPrice.replace(",", "")) > float(newPrice.replace(",", "")):
        send_fcm_notification(title, newPrice, currentPrice)
    await add_price_in_subcollection(docId=docId, current_price=newPrice)

async def add_price_in_subcollection(docId : str, current_price : str):
    today_str = str(datetime.date.today())
    await trackedProducts.document(docId).collection("priceHistory").document(today_str).set({
        "price" : current_price,
        "timestamp" : firestore_async.SERVER_TIMESTAMP
    })

async def delete_subcollection(docId : str):
    docs = trackedProducts.document(docId).collection("priceHistory").stream()

    async for doc in docs:
        await doc.reference.delete()

async def fetch_price_history(userId : str):
    docs = trackedProducts.where("currentUser", "==", userId).stream()

    price_history = []
    doc_history = []

    async for doc in docs:
        histories = doc.reference.collection("priceHistory").stream()
        async for history in histories:
            dict = history.to_dict()
            date = history.id
            price = dict["price"]
            map = {
                "date": date,
                "price": price
            }
            
            doc_history.append(map)
        price_history.append({"product" : doc.id, "history" : doc_history})
        doc_history = []

    return price_history


def send_fcm_notification(title, newPrice, currentPrice):

    token = ""
    with open("token.txt", "r") as token_file:
        token = token_file.read()
    
    if not token:
        return

    message = messaging.Message(
        token=token,
        notification=messaging.Notification(
            title=f"Price Drop Alert for {title}! 🚀",
            body=f"Price dropped from {currentPrice} to {newPrice}"
        )
    )

    try:
        response = messaging.send(message)
        print(f"Notification sent successfully: {response}")
    except Exception as e:
        print(f"Failed to send notification: {e}")