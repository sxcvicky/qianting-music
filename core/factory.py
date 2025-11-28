"""
工厂模式：转换器工厂
"""
from typing import Dict, Type, Optional
import logging
from .base import AudioConverter, AudioFormat
from .exceptions import UnsupportedFormatError

logger = logging.getLogger(__name__)


class ConverterFactory:
    """转换器工厂类"""
    
    _converters: Dict[AudioFormat, Type[AudioConverter]] = {}
    
    @classmethod
    def register(cls, input_format: AudioFormat, converter_class: Type[AudioConverter]):
        """注册转换器"""
        cls._converters[input_format] = converter_class
        logger.info(f"注册转换器: {input_format.value} -> {converter_class.__name__}")
    
    @classmethod
    def create_converter(cls, input_file: str) -> AudioConverter:
        """
        根据输入文件格式创建对应的转换器
        
        Args:
            input_file: 输入文件路径
            
        Returns:
            AudioConverter: 对应的转换器实例
            
        Raises:
            UnsupportedFormatError: 不支持的格式
        """
        try:
            input_format = AudioFormat.from_extension(input_file)
        except ValueError as e:
            raise UnsupportedFormatError(f"无法识别文件格式: {str(e)}")
        
        converter_class = cls._converters.get(input_format)
        if converter_class is None:
            raise UnsupportedFormatError(f"不支持的输入格式: {input_format.value}")
        
        return converter_class()
    
    @classmethod
    def get_supported_formats(cls) -> list[AudioFormat]:
        """获取所有支持的格式"""
        return list(cls._converters.keys())
    
    @classmethod
    def is_supported(cls, input_file: str) -> bool:
        """检查是否支持该文件格式"""
        try:
            input_format = AudioFormat.from_extension(input_file)
            return input_format in cls._converters
        except ValueError:
            return False