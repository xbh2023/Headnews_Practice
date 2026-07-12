from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from schemas.users import UserRegister, UserAuthResponse, UserInfoResponse, UpdateUserInfo, UpdateUserPassword
from crud import users
from utils import response
from utils.auth import get_current_user
from utils.response import success_reponse

# 创建APIRouter对象
router = APIRouter(prefix="/api/user", tags=["users"])


#注册用户
@router.post("/register")
async def register(
        user_data: UserRegister,
        db: AsyncSession = Depends(get_db)
):
    # 先验证用户是否存在 创建用户 生成token 响应结果
    existing_user = await users.get_users_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=400,detail="用户已存在")
    user = await users.create_user(db,user_data)
    token = await users.create_token(db,user.id)
    # return {
    #     "code": 200,
    #     "message": "success",
    #     "data": {
    #         "token": token,
    #         "userInfo":{
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    #
    # }
    response_date = UserAuthResponse(
        token=token,
        userInfo=UserInfoResponse.model_validate(user)
    )
    return success_reponse(message="注册成功",data=response_date)

#登录
@router.post("/login")
async def login(
        user_data: UserRegister,
        db: AsyncSession = Depends(get_db)
):  #登录逻辑：验证用户是否存在->验证密码->生成Token →响应结果
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=401,detail="用户名或密码错误")
    token = await users.create_token(db,user.id)
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))
    return success_reponse(
        message="登录成功",
        data=response_data
    )

#获取用户详情  参数为依赖注入
@router.get("/info")
async def get_user_info(
    user = Depends(get_current_user)
): #获取用户详情逻辑：根据用户名查询用户信息->返回结果
    return success_reponse(message="获取用户详情成功",data=UserInfoResponse.model_validate(user))

#修改用户信息 验证token 查询 用户是否存在 修改更新 定义Pydantic模型lei 响应结果
@router.put("/update")
async def update_user_info(
    update_data: UpdateUserInfo,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await users.update_user_info(db,user.username,update_data)
    return success_reponse(
        message="修改用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

@router.put("/password")
async def update_password(
    password_data: UpdateUserPassword,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    change_password = await users.update_password(
        db,
        user,
        password_data.old_password,
        password_data.new_password
    )
    if not change_password:
        raise HTTPException(status_code=500,detail="旧密码错误")
    return success_reponse(
        message="修改密码成功"
    )