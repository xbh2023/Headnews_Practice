from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest,FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_reponse

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., description="新闻ID",alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    is_favorited = await favorite.is_news_favorite(user.id, news_id,db)
    return success_reponse(
        message="查询成功",
        data=FavoriteCheckResponse(isFavorite=is_favorited)
    )
#添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    #验证用户是否登录

    result = await favorite.add_news_favorite(data.news_id,db,user.id)
    return success_reponse(
        message="收藏成功",
        data=result
    )
#取消收藏
@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., description="新闻ID",alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    data = await favorite.remove_news_favorite(news_id, db, user.id)
    if not data:
        raise HTTPException(status_code=400,detail="取消收藏失败")

    return success_reponse(
        message="取消收藏成功",

    )
#收藏列表
@router.get("/list")
async def favorite_list(
        page: int = Query(1, description="页码",ge=1),
        page_size: int = Query(10, description="每页数量",alias="pageSize",ge=1),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    total,rows = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_created_at,
        "favorite_id": favorite_id

    } for news,favorite_created_at,favorite_id in rows]
    has_more = total > page * page_size
    data = FavoriteListResponse(
        list=favorite_list,
        total=total,
        hasMore=has_more
    )
    return success_reponse(
        message="获取收藏列表查询成功",
        data=data
    )
#清空收藏列表
@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    #获取清空的收藏数量
    count = await favorite.clear_allfavorite_list(user.id, db)
    return success_reponse(
        message=f"清空收藏列表{count}条收藏记录"
    )
