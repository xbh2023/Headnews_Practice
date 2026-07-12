from typing import Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache, NEWS_LIST_KEY_PREFIX

#新闻相关的缓存方法 新闻分类的读取和写入
CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY = "new_list:"
#获取新闻分类缓存
async def get_categories_cache():
    return await get_json_cache(CATEGORIES_KEY)

#写入新闻分类缓存
#分类配置 7200  列表600  详情1800  验证码120
async def set_categories_cache(data: list[Dict[str,Any]],expire: int=7200):
    return await set_cache(CATEGORIES_KEY, data,expire)

#写入缓存--新闻列表
async def set_news_list_cache(
        category_id: Optional[int],
        page: int,
        page_size: int,
        news_list: list[Dict[str,Any]],
        expire: int=600
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return  await set_cache(key, news_list, expire)
#获取新闻列表缓存
async def get_news_list_cache(
        category_id: Optional[int],
        page: int,
        page_size: int
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)