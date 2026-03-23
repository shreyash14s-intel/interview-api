from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "data.json"

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


class Item(BaseModel):
    name: str
    role: str


# GET all items
@app.get("/items")
def get_items():
    return JSONResponse(content=read_data(), media_type="application/json")


# GET single item by id
@app.get("/items/{item_id}")
def get_item(item_id: int):
    data = read_data()
    item = next((x for x in data if x["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return JSONResponse(content=item, media_type="application/json")


# POST new item
@app.post("/items")
def create_item(item: Item):
    data = read_data()
    new_id = max((x["id"] for x in data), default=0) + 1
    new_item = {"id": new_id, **item.model_dump()}
    data.append(new_item)
    write_data(data)
    return JSONResponse(content=new_item, media_type="application/json", status_code=201)
