from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news,news_cache

# 创建APIRouter对象
router = APIRouter(prefix="/api/news", tags=["news"])

#接口实现流程
#1.模块化路由→API接口规范档
#2.定义模型类→数据库表（数据库设计文档）
#3。在crud 文件夹里面创建文件，封装操作数据库的方法
#4．在路由处理函数里面调用crud 封装好的方法，响应结果
@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 10,db: AsyncSession = Depends(get_db)):
    categories = await news_cache.get_categories(db,skip,limit)
    return {
        "code":200,
        "message":"success",
        "data": categories
    }

#获取新闻列表   /api/news/list?categoryId=&page=&pageSize=
@router.get("/list")
async def get_news_list(
        category_id: int = Query(...,title="分类id",description="分类id",alias="categoryId"),
        page: int = 1,
        page_size: int = Query(...,title="分页大小",description="分页大小",alias="pageSize"),
        db: AsyncSession = Depends(get_db)):
    news_list = await news_cache.get_news_list(db,category_id,page,page_size)
    total = await news.get_news_count(db,category_id)
    has_more =  (page-1)*page_size+len(news_list) < total
    return {
        "code":200,
        "message":"success",
        "data": {
            "list":news_list,
            "total":total,
            "hasMore":has_more
        }
    }
#获取新闻详情
@router.get("/detail")
async def get_news_detail(
        new_id: int = Query(...,title="新闻id",description="新闻id",alias="id"),
        db: AsyncSession = Depends(get_db)):
    news_detail = await news.get_news_detail(db,new_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    #await  news.increase_news_views(db,news_detail.id)
    views_res = await  news.increase_news_views(db,new_id)
    if not views_res:
        raise HTTPException(status_code=500,detail="更新浏览量失败")

    related_news = await news.get_recommend_news_list(db,news_detail.category_id,news_detail.id,5)
    return {
        "code":200,
        "message":"success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "publishTime": news_detail.publish_time.strftime("%Y-%m-%d %H:%M:%S"),
            "relateNews": related_news
        }
    }

