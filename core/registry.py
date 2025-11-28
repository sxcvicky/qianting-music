"""
转换器注册模块
自动注册所有可用的转换器
"""
import logging
import sys
from pathlib import Path
from .factory import ConverterFactory
from .base import AudioFormat

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def register_all_converters():
    """注册所有可用的转换器"""
    logger.info("开始注册所有转换器...")
    
    try:
        # 导入所有转换器
        from converters.ncm_converter import NCMConverter
        from converters.kgm_converter import KGMConverter
        from converters.ogg_converter import OGGConverter
        from converters.wav_converter import WAVConverter
        # 移除 MFLACConverter 导入（MFLAC 格式支持已下线）
        
        # 注册NCM转换器
        ConverterFactory.register(AudioFormat.NCM, NCMConverter)
        
        # 注册KGM转换器
        ConverterFactory.register(AudioFormat.KGM, KGMConverter)
        
        # 注册OGG/QMC转换器
        ConverterFactory.register(AudioFormat.OGG, OGGConverter)
        ConverterFactory.register(AudioFormat.QMC, OGGConverter)
        ConverterFactory.register(AudioFormat.QMC0, OGGConverter)
        ConverterFactory.register(AudioFormat.QMC3, OGGConverter)
        ConverterFactory.register(AudioFormat.QMCFLAC, OGGConverter)
        
        # 注册WAV转换器
        ConverterFactory.register(AudioFormat.WAV, WAVConverter)
        
        # MFLAC 格式不可转换，故不再注册对应转换器
        
        logger.info(f"转换器注册完成，共注册 {len(ConverterFactory.get_supported_formats())} 种格式")
        logger.info(f"支持的格式: {[fmt.value for fmt in ConverterFactory.get_supported_formats()]}")
        
    except ImportError as e:
        logger.error(f"导入转换器失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"注册转换器时出错: {str(e)}")
        raise


def get_converter_info():
    """获取转换器信息"""
    info = {
        'supported_formats': [fmt.value for fmt in ConverterFactory.get_supported_formats()],
        'total_converters': len(ConverterFactory._converters),
        'format_mapping': {fmt.value: cls.__name__ for fmt, cls in ConverterFactory._converters.items()}
    }
    return info
