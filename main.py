# FastAPI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
# APP
from app.routers import imagesRouter, usersRouter, adminRouter
from app.security import secureuser
from app.DB.db import create_db_table

app = FastAPI()
app.title = "Pic Profile Maker"
app.version = "0.1.0"


app.include_router(usersRouter.router, 
                   prefix='/users',
                   tags=['Users'])
app.include_router(imagesRouter.router,
                   prefix='/pictures',
                   tags=['Pictures'])   
app.include_router(adminRouter.router,
                   prefix='/admin',
                   tags=['Admin'])
app.include_router(secureuser.router)

@app.on_event('startup')
def on_startup():
    """
    Initializes the app on startup and creates a database table.
    :param: None
    :return: None
    """
    create_db_table()

@app.get(path="/",tags=["Home"])
def home():
    """
    Returns an HTMLResponse containing a h1 tag with the text "Pic Profile Maker".
    """
    return HTMLResponse('<h1>Pic Profile Maker</h1>')