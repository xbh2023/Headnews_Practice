import uvicorn
from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers

app = FastAPI()


register_exception_handlers(app)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

# ========== 跨域核心配置 ==========
app.add_middleware(
    CORSMiddleware,
    # 允许访问的前端地址，端口必须和你Vue启动的端口一致
    allow_origins=[
        "http://localhost:5173",   # Vue3 Vite默认端口
        "http://localhost:8080",   # Vue2 CLI默认端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,   # 允许携带Cookie、Token等认证信息
    allow_methods=["*"],      # 允许所有HTTP方法（GET/POST/PUT/DELETE等）
    allow_headers=["*"],      # 允许所有请求头（含Authorization）
)
#挂在路由 
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host= "0.0.0.0", port=8000, reload=True)