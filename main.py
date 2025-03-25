from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import web_scraping
from models.TrackedProductModel import TrackedProduct
from models.UserIdModel import UserId
from models.LinkProductModel import LinkProduct
from models.TokenModel import Token
from firebase_methods import add_product, delete_product, is_product_tracked, fetch_price_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH"],  # Only allow required methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/fetch-deals/") # fetches current deals
async def fetch_deals():
    try:
        deals = web_scraping.deals_scraping()
        json = {
            "deals": deals
        }
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/fetch-data/{query}") # fetches products after scraping
async def fetch_data(query : str):
    try:
        amazon_list = web_scraping.amazon_scraping(query)
        flipkart_list = web_scraping.flipkart_scraping(query)
        json = {
            "amazon": amazon_list,
            "flipkart": flipkart_list
        }
        return json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-product/") # adds the products in the db
async def add_tracked_product(tracked_product : TrackedProduct):
    try:
        await add_product(tracked_product)
        json = {"result": "Product added successfully"}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete-product/{docId}/") # deletes the product in db
async def delete_tracked_product(docId : str):
    try:
        await delete_product(docId)
        json = {"result": "Product deleted successfully"}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/is-product-tracked/{docId}/") # returns whether the product is in db or not
async def check_product_tracked(docId : str):
    try:
        result = await is_product_tracked(docId)
        json = {"result": result}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/add-product-by-link/") #this creates a new entry in db when user enter links it scrapes and then add the info
async def add_product_by_link(link_product : LinkProduct):
    json = {}
    try:
        if link_product.productUrl.startswith("https://www.amazon.in"):
            result = await web_scraping.fetch_amazon_product(link_product.productUrl, link_product.currentUser)
            if result == "Exists":
                json = {"result": "Product already exists"}
                return json
            elif result == "Added":
                json = {"result": "Product added successfully"}
                return json
        elif link_product.productUrl.startswith("https://www.flipkart.com"):
            result = await web_scraping.fetch_flipkart_product(link_product.productUrl, link_product.currentUser)
            if result == "Exists":
                json = {"result": "Product already exists"}
                return json
            elif result == "Added":
                print("results")
                json = {"result": "Product added successfully"}
                return json
        else:
            json = {"result": "Provide supported link"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/fetch-latest-price-from-app/") # this fetches latest price by scraping and updates the db or creates new entry
async def fetch_latest_price_from_app(userId : UserId):
    json = {}
    try:
        await web_scraping.fetch_latest_price_from_app(userId.userId)
        json = {"result" : "Price updated successfully"}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/fetch-price-history/{userId}/")
async def fetch_price_history_of_product(userId):
    try:
        price_history = await fetch_price_history(userId)
        return JSONResponse(content=price_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/update-token/")
async def update_token(token : Token):
    try:
        saved_token = ""
        with open("token.txt", "r") as device_token:
            saved_token = device_token.read()

        if saved_token != token.token:
            with open("token.txt", "w") as device_token:
                device_token.write(token.token)

            return {"message": "Token updated"}
        else:
            return {"message": "Token is same"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        