"""
音频格式转换器核心模块

提供基础抽象类、工厂模式和通用工具
"""

from .base import AudioConverter, ConversionResult, AudioFormat
from .factory import ConverterFactory
from .exceptions import ConversionError, UnsupportedFormatError, FileNotFoundError
from .registry import register_all_converters, get_converter_info

__all__ = [
    'AudioConverter',
    'ConversionResult', 
    'AudioFormat',
    'ConverterFactory',
    'ConversionError',
    'UnsupportedFormatError',
    'FileNotFoundError',
    'register_all_converters',
    'get_converter_info'
]