from pydantic import BaseModel

# Pydanticモデル
class ItemResponse(BaseModel):
    id: int
    param1: float
    param2: float
    param3: float
    name: str

    class Config:
        orm_mode = True

