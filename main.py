from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import web_scraping # import amazon_scraping, flipkart_scraping, deals_scraping, fetch_amazon_product
from models.UserInputModel import UserInput
from models.TrackedProductModel import TrackedProduct
from models.LinkProductModel import LinkProduct
from firebase_methods import add_product, delete_product, is_product_tracked

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only allow required methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/fetch-deals/")
async def fetch_deals():
    try:
        deals = web_scraping.deals_scraping()
        json = {
            "deals": deals
        }
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/fetch-data/")
async def fetch_data(user_input : UserInput):
    try:
        amazon_list = web_scraping.amazon_scraping(user_input.query)
        flipkart_list = web_scraping.flipkart_scraping(user_input.query)
        json = {
            "amazon": amazon_list,
            "flipkart": flipkart_list
        }
        return json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-product/")
async def add_tracked_product(tracked_product : TrackedProduct):
    try:
        await add_product(tracked_product)
        json = {"result": "Product added successfully"}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete-product/{docId}/")
async def delete_tracked_product(docId : str):
    try:
        await delete_product(docId)
        json = {"result": "Product deleted successfully"}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/is-product-tracked/{docId}/")
async def check_product_tracked(docId : str):
    try:
        result = await is_product_tracked(docId)
        json = {"result": result}
        return json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/add-product-by-link/")
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
                json = {"result": "Product added successfully"}
                return json
        else:
            json = {"result": "Provide supported link"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))