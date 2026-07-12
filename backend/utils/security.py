from passlib.context import CryptContext

# 直接使用内置的 bcrypt_sha256，自动处理 72 字节限制
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
