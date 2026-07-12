import asyncio
from config.cache_conf import set_cache, get_json_cache

async def test_redis():
    await set_cache("news:categories", [{"id": 1, "name": "测试分类"}], 7200)
    val = await get_json_cache("news:categories")
    print(val)
    return val

if __name__ == "__main__":
    asyncio.run(test_redis())
