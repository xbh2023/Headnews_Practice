from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger
from models.history import History
from models.news import News


#添加浏览记录 验证登录 检查是否浏览过当前新闻 如果是则更新浏览时间 否则添加浏览记录
async def add_news_history(
        news_id,
        id: int,
        db: AsyncSession
):
    query = select(History).where(History.user_id == id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

    return None

#获取浏览记录列表
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    history_query = (select(News,History.view_time.label("view_time"),History.id.label("history_id")).join(History, History.news_id == News.id)
                     .where(History.user_id == user_id)
                     .order_by(History.view_time.desc())
                     .offset((page-1) * page_size).limit(page_size))
    result = await db.execute(history_query)
    rows = result.all()

    return total, rows
#删除单个浏览记录
async def delete_only_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    try:
        delete_query = delete(History).where(
            History.news_id == news_id,
        History.user_id == user_id
        )
        result = await db.execute(delete_query)
        # print(f"删除浏览记录结果: {result.rowcount}")
        logger.info(f"删除浏览记录 | 用户ID:{user_id} | 新闻ID:{news_id} | 受影响行数:{result.rowcount}")
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        logger.error(f"删除浏览记录异常 | 用户ID:{user_id} | 新闻ID:{news_id} | 异常信息:{e}")
        raise e

#清空浏览记录
async def clear_history_list(
        user_id: int,
        db: AsyncSession
):
    delete_query = delete(History).where(History.user_id == user_id)
    result = await db.execute(delete_query)
    await db.commit()
    return result.rowcount or 0
