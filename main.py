from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from web_scraping import amazon_scraping, flipkart_scraping

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow required methods
    allow_headers=["*"],  # Allow all headers
)

class UserInput(BaseModel):
    query : str

@app.post("/fetchData/")
async def fetchData(user_input : UserInput):
    try:
        amazon_list = amazon_scraping(user_input.query)
        flipkart_list = flipkart_scraping(user_input.query)
        return {
            "amazon": amazon_list,
            "flipkart": flipkart_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))