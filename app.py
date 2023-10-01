import fastapi_loki_tempo
import random
import asyncio
import logging
from fastapi import Request, FastAPI

app = FastAPI()
fastapi_loki_tempo.patch(app=app)


@app.get('/')
async def index(request: Request = None):
    return {'message': 'hello'}


@app.get('/random')
async def index(
    minimum: float = 0.1,
    maximum: float = 2.0,
    request: Request = None,
):
    how_long = random.uniform(0.1, 2.0)
    logging.info(f'I sleep for {how_long} seconds')
    await asyncio.sleep(how_long)
    return {'message': f'sleep for {how_long} seconds'}
