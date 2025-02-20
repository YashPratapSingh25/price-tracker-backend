from fastapi import FastAPI, HTTPException
from web_scraping import amazon_scraping, flipkart_scraping

app = FastAPI()

@app.post("/fetchData/")
async def fetchData(user_input : str):
    try:
        amazon_list = amazon_scraping(user_input)
        flipkart_list = flipkart_scraping(user_input)
        return {
            "amazon": amazon_list,
            "flipkart": flipkart_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))