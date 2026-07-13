import logging
import os
from logging.handlers import TimedRotatingFileHandler

# 日志文件存放目录（自动创建在 backend/logs/ 下）
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志输出格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "app") -> logging.Logger:
    """
    获取统一配置的日志实例，全局单例，避免重复添加处理器
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # 全局日志级别
    logger.setLevel(logging.INFO)

    # 1. 控制台输出处理器（开发调试用）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(console_handler)

    # 2. 文件输出处理器（按天切割，保留7天历史日志）
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        when="D",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(file_handler)

    return logger


# 全局默认日志实例，业务代码直接导入即可使用
logger = get_logger()
