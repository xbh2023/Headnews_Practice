
from datetime import timedelta, datetime
from fastapi import HTTPException
from models.users import User, UserToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
import uuid
from schemas.users import UserRegister, UpdateUserInfo
from utils import security

#根据用户名查询数据库
async def get_users_by_username(db: AsyncSession,username: str):
    select_stmt = select(User).where(User.username == username)
    result = await db.execute(select_stmt)
    user = result.scalar_one_or_none()
    return user

#创建用户
async def create_user(
        db: AsyncSession,
        user_data: UserRegister
):
    #加密
    userhash_password = security.get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        password=userhash_password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return  user

#生成token
async def create_token(
        db: AsyncSession,
        user_id: int
): #生成token 设置过期时间 查询当前 用户是否有令牌 有令牌则更新令牌 无令牌则创建令牌
    newtoken = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    select_stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(select_stmt)
    user_token = result.scalar_one_or_none()
    if user_token:
        update_stmt = update(UserToken).where(UserToken.user_id == user_id).values(
            token=newtoken,
            expires_at=expires_at
        )
        await db.execute(update_stmt)
        await db.commit()
    else:
        user_token = UserToken(
            user_id=user_id,
            token=newtoken,
            expires_at=expires_at
        )
        db.add(user_token)
        await db.commit()
    print("生成token成功", newtoken)
    return  newtoken


async def authenticate_user(db:AsyncSession, username:str, password:str):
    user = await get_users_by_username(db,username)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None

    return user

#根据token 查询用户验证用户
async def get_user_by_token(db: AsyncSession, token: str):
    select_stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(select_stmt)
    user_token = result.scalar_one_or_none()
    if not user_token or user_token.expires_at < datetime.now():
        return None
    user_query = select(User).where(User.id == user_token.user_id)
    result = await db.execute(user_query)
    return result.scalar_one_or_none()


async def update_user_info(
        db:AsyncSession,
        username:str,
        user_data: UpdateUserInfo
):
    update_stmt = update(User).where(User.username == username).values(
        **user_data.model_dump(exclude_unset=True,exclude_none= True)
    )
    result = await db.execute(update_stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=400,detail="更新用户信息失败")
    user = await get_users_by_username(db,username)

    return user


async def update_password(
        db: AsyncSession,
        user:User,
        old_password: str,
        new_password: str
):  #验证用户是否登录 验证用户密码 一致 则更新密码
    if not security.verify_password(old_password,user.password):
        raise HTTPException(status_code=400,detail="旧密码错误")
    hash_password = security.get_password_hash(new_password)
    # update_stmt = update(User).where(User.id == user.id).values(
    #     password=hash_password
    # )
    user.password = hash_password
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return True