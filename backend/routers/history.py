from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.hsitory import HistoryAddRequest
from utils.auth import get_current_user
from utils.response import success_reponse

router = APIRouter(prefix="/api/history", tags=["history"])

#添加浏览记录
@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.add_news_history(data.news_id,user.id,db)
    return success_reponse(
        message="添加浏览记录成功",
        data=result
    )
#获取浏览记录列表
@router.get("/list")
async def history_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        page: int = Query(1, description="页码",ge=1),
        page_size: int = Query(10, description="每页数量",alias="pageSize",ge=1)

):
    total,rows = await history.get_history_list(db, user.id, page, page_size)
    history_list = [
        {
            **news.__dict__,
            "view_time": view_time,
            "history_id": history_id
        }
        for news,view_time,history_id in rows
    ]
    has_more = total > page * page_size
    data = {
        "list": history_list,
        "total": total,
        "hasMore": has_more
    }
    return success_reponse(
        message="获取浏览记录列表成功",
        data=data
    )
#删除单个浏览记录
@router.delete("/delete/{news_id}")
async def delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.delete_only_history(news_id,user.id,db)
    print(result)
    if not result:
        raise HTTPException(status_code=400,detail="删除失败")
    return success_reponse(
        message="删除成功"
    )
#清空浏览记录
@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await history.clear_history_list(user.id,db)
    return success_reponse(
        message=f"清空浏览记录{count}条浏览记录"
    )
