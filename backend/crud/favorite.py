
from sqlalchemy import select, delete, func, join
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News
from models.users import User
from utils.auth import get_current_user


async def is_news_favorite(
        user_id: int,
        news_id: int,
        db: AsyncSession
):
    favorite_where = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(favorite_where)
    favorite = result.scalar_one_or_none()
    return favorite is not None


async def add_news_favorite(
        news_id: int,
        db: AsyncSession,
        user_id: int,
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
        news_id: int,
        db: AsyncSession,
        user_id: int,
)->bool:
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
                    Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    # rowcount 表示本次操作影响的行数，大于 0 说明删除成功
    return result.rowcount > 0

async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int =1,
        page_size: int = 10
):
    #获取收藏总量 +列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    #获取列表 连表查询
    favorite_query = (select(
        News,
        Favorite.created_at.label("favorite_created_at")
        ,Favorite.id.label("favorite_id"))
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
        .offset((page-1) * page_size))
    result = await db.execute(favorite_query)
    rows = result.all()
    return total,rows
#清空收藏列表
async def clear_allfavorite_list(
        user_id: int,
        db: AsyncSession
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0