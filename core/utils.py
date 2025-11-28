"""
通用工具函数
"""
import os
import logging
from typing import Optional


def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None):
    """设置日志配置"""
    handlers = []
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # 文件输出
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）"""
    return os.path.getsize(file_path) / (1024 * 1024)


def ensure_directory(directory: str) -> None:
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)


def validate_file_path(file_path: str) -> bool:
    """验证文件路径"""
    return os.path.exists(file_path) and os.path.isfile(file_path)


def calculate_progress(current: int, total: int) -> int:
    """计算进度百分比"""
    if total == 0:
        return 0
    return min(100, max(0, int(current * 100 / total)))