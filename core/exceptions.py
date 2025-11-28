"""
自定义异常类
"""


class ConversionError(Exception):
    """转换过程中的错误"""
    pass


class UnsupportedFormatError(ConversionError):
    """不支持的文件格式错误"""
    pass


class FileNotFoundError(ConversionError):
    """文件未找到错误"""
    pass


class InvalidHeaderError(ConversionError):
    """无效文件头错误"""
    pass


class DecryptionError(ConversionError):
    """解密错误"""
    pass


class MetadataError(ConversionError):
    """元数据处理错误"""
    pass