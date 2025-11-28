"""
应用配置管理
"""
import os
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AppSettings:
    """应用设置数据类"""
    # 路径设置
    default_output_dir: str = ""
    last_input_dir: str = ""
    last_output_dir: str = ""
    
    # 转换设置
    default_output_format: str = "mp3"
    audio_quality: str = "normal"  # low, normal, high
    preserve_metadata: bool = True
    overwrite_existing: bool = False
    
    # 界面设置
    window_width: int = 800
    window_height: int = 600
    window_x: int = -1  # -1 表示居中
    window_y: int = -1  # -1 表示居中
    theme: str = "default"
    language: str = "zh_CN"
    
    # 日志设置
    log_level: str = "INFO"
    enable_file_logging: bool = True
    max_log_files: int = 10
    max_log_size_mb: int = 50
    
    # 性能设置
    max_concurrent_conversions: int = 1
    chunk_size_mb: int = 1
    
    # 高级设置
    enable_debug_mode: bool = False
    auto_check_updates: bool = True
    send_usage_statistics: bool = False


def get_config_dir() -> Path:
    """获取配置目录"""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.getenv('APPDATA', '')) / 'AudioConverter'
    else:  # Linux/macOS
        config_dir = Path.home() / '.config' / 'audioconverter'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """获取配置文件路径"""
    return get_config_dir() / 'settings.json'


def get_default_settings() -> AppSettings:
    """获取默认设置"""
    # 设置默认输出目录
    default_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    settings = AppSettings()
    settings.default_output_dir = default_output
    settings.last_output_dir = default_output
    
    return settings


def load_settings() -> AppSettings:
    """加载设置"""
    config_file = get_config_file()
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建默认设置
            settings = get_default_settings()
            
            # 更新已有的设置
            for key, value in data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            logger.info(f"设置已从文件加载: {config_file}")
            return settings
            
        else:
            logger.info("配置文件不存在，使用默认设置")
            return get_default_settings()
            
    except Exception as e:
        logger.error(f"加载设置失败: {str(e)}")
        logger.info("使用默认设置")
        return get_default_settings()


def save_settings(settings: AppSettings) -> bool:
    """保存设置"""
    try:
        config_file = get_config_file()
        
        # 确保配置目录存在
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为字典并保存
        data = asdict(settings)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"设置已保存到: {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"保存设置失败: {str(e)}")
        return False


def reset_settings() -> AppSettings:
    """重置为默认设置"""
    settings = get_default_settings()
    save_settings(settings)
    logger.info("设置已重置为默认值")
    return settings


def update_setting(key: str, value: Any) -> bool:
    """更新单个设置项"""
    try:
        settings = load_settings()
        if hasattr(settings, key):
            setattr(settings, key, value)
            return save_settings(settings)
        else:
            logger.warning(f"未知的设置项: {key}")
            return False
    except Exception as e:
        logger.error(f"更新设置失败: {str(e)}")
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """获取单个设置项"""
    try:
        settings = load_settings()
        return getattr(settings, key, default)
    except Exception as e:
        logger.error(f"获取设置失败: {str(e)}")
        return default


def validate_settings(settings: AppSettings) -> list[str]:
    """验证设置有效性"""
    errors = []
    
    # 验证目录路径
    if settings.default_output_dir and not os.path.isdir(os.path.dirname(settings.default_output_dir)):
        errors.append("默认输出目录的父目录不存在")
    
    # 验证数值范围
    if settings.window_width < 400 or settings.window_width > 3840:
        errors.append("窗口宽度超出有效范围 (400-3840)")
    
    if settings.window_height < 300 or settings.window_height > 2160:
        errors.append("窗口高度超出有效范围 (300-2160)")
    
    if settings.max_concurrent_conversions < 1 or settings.max_concurrent_conversions > 16:
        errors.append("最大并发转换数超出有效范围 (1-16)")
    
    if settings.chunk_size_mb < 1 or settings.chunk_size_mb > 100:
        errors.append("数据块大小超出有效范围 (1-100 MB)")
    
    # 验证枚举值
    valid_formats = ['mp3', 'flac', 'wav']
    if settings.default_output_format not in valid_formats:
        errors.append(f"无效的默认输出格式: {settings.default_output_format}")
    
    valid_qualities = ['low', 'normal', 'high']
    if settings.audio_quality not in valid_qualities:
        errors.append(f"无效的音频质量设置: {settings.audio_quality}")
    
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if settings.log_level not in valid_log_levels:
        errors.append(f"无效的日志级别: {settings.log_level}")
    
    return errors