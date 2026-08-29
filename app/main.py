from fastapi import FastAPI 
from . import models
from .database import engine, sessionLocal, get_db
from .router import post, users, auth
from .config import settings

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

# while True:
#     try:
#         conn = psycopg.connect(
#             host = 'localhost', 
#             dbname = 'fastapi', 
#             user = 'postgres',
#             password = 'apple',
#             row_factory= dict_row
#         )
#         cursor = conn.cursor()
#         print("database connected successfully")
#         break
#     except Exception as error:
#         print("connecting to database failed!")
#         print("Error: ", error)
#         time.sleep(2)


app.include_router(post.router)
app.include_router(users.router)
app.include_router(auth.router)


