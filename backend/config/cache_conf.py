import json

import redis.asyncio as redis


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
#创建redis的；连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)
#封装缓存操作 设置和读取（字符串和列表或字典）
#读取字符串
async def get_cache(key: str):
    try:
        if await redis_client.exists(key):
            return await redis_client.get(key)
    except Exception as e:
        print(e)
        return None

#读取列表或者字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print("获取缓存失败")
        print(e)
        return None

#设置缓存
async def set_cache(key: str, value: str,expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, expire)
        return True
    except Exception as e:
        print("设置缓存失败")
        print(e)
        return False

# ===================== 通用缓存清理工具 =====================
async def delete_cache(key: str) -> bool:
    """删除单个指定缓存key"""
    try:
        count = await redis_client.delete(key)
        return count > 0
    except Exception as e:
        print(f"删除缓存[{key}]失败:", e)
        return False

async def delete_cache_batch(keys: list[str]) -> bool:
    """批量删除多个指定缓存key"""
    if not keys:
        return True
    try:
        count = await redis_client.delete(*keys)
        return count > 0
    except Exception as e:
        print("批量删除缓存失败:", e)
        return False

async def delete_cache_by_prefix(prefix: str) -> bool:
    """按前缀模糊删除缓存
    采用 scan 遍历，避免大数量级下阻塞 Redis
    """
    try:
        keys = []
        async for key in redis_client.scan_iter(match=f"{prefix}*"):
            keys.append(key)
        if keys:
            await redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"按前缀[{prefix}]删除缓存失败:", e)
        return False

async def delay_delete_cache(key: str, delay: float = 0.5):
    """延迟双删工具：先立即删一次，等待 delay 秒后再删一次
    解决并发场景下「删缓存后，旧读请求刚好把老数据写回缓存」的脏数据问题
    """
    await delete_cache(key)

    async def _delay_del():
        await asyncio.sleep(delay)
        await delete_cache(key)

    # 后台异步执行，不阻塞主接口返回
    asyncio.create_task(_delay_del())

# ===================== 业务缓存Key统一管理 =====================
CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY_PREFIX = "news:list:"
NEWS_DETAIL_KEY_PREFIX = "news:detail:"