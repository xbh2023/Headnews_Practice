from cache.news_cache import get_news_list_cache, set_news_list_cache
from models.news import Category,News
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update


async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 10):
    #select_stmt = select(Category).offset(skip).limit(limit)
    select_stmt = select( Category).offset(skip).limit(limit)
    categories = await db.execute(select_stmt)
    scalars__all = categories.scalars().all()
    return scalars__all

#如果只写 limit(10)，那每次查的都是前 10 条，翻页永远停在第一页。
#offset 负责定位起点，limit 负责控制长度，两者合起来才能实现翻页。
async def get_news_list(db: AsyncSession,category_id: int,page: int,page_size: int):
    select_stmt = select(News).where(News.category_id == category_id).offset((page-1)*page_size).limit(page_size)
    result = await db.execute(select_stmt)
    result_all = result.scalars().all()

    return result_all

#获取新闻总量
async def get_news_count(db: AsyncSession,category_id: int):
    select_stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(select_stmt)
    return result.scalar_one()

#当前新闻详情+增加一次浏览量+相关新闻（同分类id的新闻）
#获取新闻详情
async def get_news_detail(db: AsyncSession,news_id: int):
    select_stmt = select(News).where(News.id == news_id)
    result = await db.execute(select_stmt)
    news = result.scalar_one_or_none()
    return news
# 增加浏览量
async def increase_news_views(db: AsyncSession,news_id: int):
    values = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(values)
    await db.commit()
    #检查数据库中数据是否更新成功
    return result.rowcount>0
   # return await get_news_detail(db,news_id)
#获取推荐新闻列表
async def get_recommend_news_list(db: AsyncSession,category_id: int,news_id: int,limit: int):
    select_stmt = select(News).where(News.category_id == category_id and News.id != news_id).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(select_stmt)
    related_news = result.scalars().all()
    #列表推导式 推导新闻核心数据

    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "publishTime": news_detail.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
    } for news_detail in related_news]