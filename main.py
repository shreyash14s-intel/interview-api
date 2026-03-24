from fastapi import FastAPI, HTTPException, Query
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

DEFAULT_PAGE_SIZE = 50

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


# GET all items with pagination
# Query params: page (1-based), page_size (default 10)
# Example: /items?page=2&page_size=5
@app.get("/items")
def get_items(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100, description="Number of items per page"),
):
    data = read_data()
    total = len(data)
    total_pages = max(1, -(-total // page_size))  # Ceiling division

    # Validate requested page does not exceed total pages
    if page > total_pages:
        raise HTTPException(
            status_code=404,
            detail=f"Page {page} does not exist. Total pages: {total_pages}"
        )

    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = data[start:end]

    return JSONResponse(
        content={
            "data": paginated_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        media_type="application/json",
    )


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
