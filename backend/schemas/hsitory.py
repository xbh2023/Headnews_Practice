from pydantic import BaseModel, Field, ConfigDict


#添加浏览记录模型类
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")
    model_config = ConfigDict(
        populate_by_name=True
    )