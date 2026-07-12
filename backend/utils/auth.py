from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import users

#根据token 查询用户 返回用户
async def get_current_user(
        authorization: str = Header(...,alias="Authorization"),
        db: AsyncSession = Depends(get_db)
):
    print("token",authorization)
    # token = authorization.split(" ")[1]
    token = authorization
    print("分隔开后token",token)
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401,detail="无效或过期令牌")
    return user