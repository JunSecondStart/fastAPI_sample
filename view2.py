from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional, Any
from pydantic import BaseModel

app = FastAPI()

# グローバル変数でフラグを保持
state = {
    "get3_executed": False
}

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# テンプレートディレクトリの設定
templates = Jinja2Templates(directory="templates")

# SQLite3 データベース接続設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./your_database_name.db"
SQLALCHEMY_DATABASE_URL2 = "sqlite:///./got_data.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

engine2 = create_engine(SQLALCHEMY_DATABASE_URL2, connect_args={"check_same_thread": False})
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine2)

# Pydanticモデル
class ItemResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

# Pydanticモデル
class DataResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db2():
    db2 = SessionLocal2()
    try:
        yield db2
    finally:
        db2.close()

@app.get("/items/", response_class=HTMLResponse)
async def read_items(request: Request, id: Optional[int] = Query(None, description="Filter by id"), db: Session = Depends(get_db)) -> Any:
    if id is not None:
        items = db.query(Item).filter(Item.id == id).all()
    else:
        items = db.query(Item).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")

    items_response = [ItemResponse.from_orm(item).dict() for item in items]

    return templates.TemplateResponse(
            request=request,
            name="items.html",
            context={"items": items_response}
        )


@app.get("/transfer_items/")
def transfer_items(request: Request, id: Optional[int] = Query(None, description="Filter by id"), db1: Session = Depends(get_db), db2: Session = Depends(get_db2)):
    if not state["get3_executed"]:
        raise HTTPException(status_code=403, detail="GET 3 must be executed before GET 2")
    else:
        if id is not None:
            items = db1.query(Item).filter(Item.id == id).all()
        else:
            items = db1.query(Item).all()

    if not items:
        raise HTTPException(status_code=404, detail="Items not found")

    for item in items:
        db_item = Data(
            param1=item.param1,
            param2=item.param2,
            param3=item.param3,
            name=item.name
        )
        db2.add(db_item)
    db2.commit()
    
    state["get3_executed"] = False
    
    return {"message": "Items transferred successfully"}


@app.get("/transfer_items/data/", response_class=HTMLResponse)
async def read_data(request: Request, id: Optional[int] = Query(None, description="Filter by id"), db: Session = Depends(get_db2)) -> Any:
    if id is not None:
        datas = db.query(Data).filter(Data.id == id).all()
    else:
        datas = db.query(Data).all()
    
    if not datas:
        raise HTTPException(status_code=404, detail="Datas not found")

    datas_response = [DataResponse.from_orm(data).dict() for data in datas]

    state["get3_executed"] = True

    return templates.TemplateResponse(
            request=request,
            name="data.html",
            context={"datas": datas_response}
        )

# フラグをリセットするエンドポイント（開発用）
@app.get("/reset")
def reset_state():
    state["get3_executed"] = False
    return {"message": "State has been reset"}







# サーバーの起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

