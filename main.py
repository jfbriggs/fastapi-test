from fastapi import FastAPI, Query, Path, Body
from typing import Dict, Optional, List, Set
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(None, title="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: Set[str] = []
    images: Optional[List[Image]] = None


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello World"}


@app.post("/items/")
async def create_item(item: Item) -> dict:
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: int = Body(..., gt=0), q: Optional[str] = None
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/")
async def read_items(q: str = Query(..., title="Query string", description="Query string for items to search in db", min_length=3, deprecated=True)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.put("/item2s/{item_id}")
async def update_item2(item_id: int, item: Item = Body(..., embed=True)):  # will expect "item" key in req body with Item fields inside dict as value
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/items2/")
async def read_items2(q: Optional[List[str]] = Query(["foo", "bar"], alias="item-query")):
    query_items = {"q": q}
    return query_items


@app.get("/items/{item_id}")
async def read_item(
        *,
        item_id: int = Path(..., title="The ID of item to get", gt=1, le=1000),
        q: str,
        size: float = Query(..., gt=0, lt=10.5)
) -> Dict[str, int]:
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple")
async def create_multiple_images(images: List[Image]):
    return images


@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
