import math

import h5py
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, PositiveInt, conlist, confloat


tags_metadata = [
    {
        "name": "add",
        "description": "Append values into a pool. Create if the pool is not existed.",
    },
    {
        "name": "query",
        "description": "Get total amount of element and the calculated quantile of choice of a pool.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


class StatusResponse(BaseModel):
    status: str


class PoolAddItem(BaseModel):
    poolId: PositiveInt
    poolValues: conlist(float, min_items=1)


class PoolQueryItem(BaseModel):
    poolId: PositiveInt
    percentile: confloat(gt=0, le=100)


class PoolQueryResponse(BaseModel):
    quantile: float
    total: int


def percentile(percentile: float, data: np.ndarray):
    data_ = np.sort(data, kind="mergesort")
    n = len(data_)
    p = percentile * n / 100
    if p.is_integer():
        return int(data_[int(p) - 1]), n
    else:
        return int(data_[int(math.ceil(p)) - 1]), n


@app.get("/health-check", response_model=StatusResponse)
async def health_check():
    return {"status": "OK"}


@app.post("/add", response_model=StatusResponse, tags=["add"])
async def add(item: PoolAddItem):
    if len(item.poolValues) == 0:
        return {"status": "error", "message": "poolValues must have more than 1 values"}

    with h5py.File("pools.hdf5", "a") as p:
        pid = str(item.poolId)
        if pid not in p:
            add_type = "inserted"
            p.create_dataset(pid, data=item.poolValues, dtype="i8", maxshape=(None,), chunks=True)
        else:
            add_type = "appended"
            p[pid].resize((len(p[pid]) + len(item.poolValues),))
            p[pid][-len(item.poolValues):] = np.array(item.poolValues)
    return {"status": add_type}


@app.post("/query", response_model=PoolQueryResponse, tags=["query"])
async def query(item: PoolQueryItem):
    pid = str(item.poolId)

    with h5py.File("pools.hdf5", "a") as p:
        if pid not in p:
            return {"error": "PoolID does not exist"}
        values = p[pid][...]

    q, n = percentile(item.percentile, values)
    return {"quantile": q, "total": n}


@app.delete("/delete/{pool_id}", response_model=StatusResponse)
async def delete(pool_id: int):
    pid = str(pool_id)

    with h5py.File("pools.hdf5", "a") as p:
        if pid not in p:
            return {"status": "error", "message": f"Pool ID {pool_id} does not exist"}
        del p[pid]

    return {"status": "deleted"}

