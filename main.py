from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:@localhost/your_database_name"

# SQLAlchemyの設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# Pydanticモデル
class ItemResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True

@app.get("/items/", response_model=List[ItemResponse])
def read_items(param1: float = Query(...), param2: float = Query(...), param3: float = Query(...)):
    session = SessionLocal()
    items = session.query(Item).filter(
        Item.param1 == param1,
        Item.param2 == param2,
        Item.param3 == param3
    ).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    
    return items

# 例としてのデータ挿入エンドポイント（テスト用）
@app.post("/items/")
def create_item(name: str, param1: float, param2: float, param3: float):
    session = SessionLocal()
    item = Item(name=name, param1=param1, param2=param2, param3=param3)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# サーバーの起動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
