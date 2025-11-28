"""
基础抽象类和数据结构
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, Callable
import os
import logging

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """支持的音频格式枚举"""
    KGM = "kgm"
    NCM = "ncm" 
    OGG = "ogg"
    QMC = "qmc"
    QMC0 = "qmc0"
    QMC3 = "qmc3"
    QMCFLAC = "qmcflac"
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    # 说明：MFLAC 已移除，因新版格式不可转换
    
    @classmethod
    def from_extension(cls, file_path: str) -> 'AudioFormat':
        """从文件扩展名获取格式"""
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        for format_type in cls:
            if format_type.value == ext:
                return format_type
        raise ValueError(f"不支持的文件格式: {ext}")
    
    @property
    def is_encrypted(self) -> bool:
        """判断是否为加密格式"""
        return self in [self.KGM, self.NCM, self.OGG, self.QMC,
                        self.QMC0, self.QMC3, self.QMCFLAC]


@dataclass
class ConversionResult:
    """转换结果数据结构"""
    success: bool
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __bool__(self) -> bool:
        return self.success


@dataclass 
class AudioMetadata:
    """音频元数据"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track: Optional[int] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None


class AudioConverter(ABC):
    """音频转换器基础抽象类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    @abstractmethod
    def supported_input_formats(self) -> list[AudioFormat]:
        """支持的输入格式"""
        pass
    
    @property
    @abstractmethod
    def supported_output_formats(self) -> list[AudioFormat]:
        """支持的输出格式"""
        pass
    
    @abstractmethod
    def convert(self, input_file: str, output_dir: str, 
                output_format: AudioFormat = AudioFormat.MP3,
                progress_callback: Optional[Callable[[int], None]] = None) -> ConversionResult:
        """
        转换音频文件
        
        Args:
            input_file: 输入文件路径
            output_dir: 输出目录
            output_format: 输出格式，默认MP3
            progress_callback: 进度回调函数
            
        Returns:
            ConversionResult: 转换结果
        """
        pass
    
    def validate_input(self, input_file: str) -> bool:
        """验证输入文件"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        if not os.path.isfile(input_file):
            raise ValueError(f"输入路径不是文件: {input_file}")
        
        try:
            input_format = AudioFormat.from_extension(input_file)
            if input_format not in self.supported_input_formats:
                raise ValueError(f"不支持的输入格式: {input_format.value}")
        except ValueError as e:
            raise ValueError(f"文件格式验证失败: {str(e)}")
        
        return True
    
    def ensure_output_dir(self, output_dir: str) -> None:
        """确保输出目录存在"""
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"输出目录无写入权限: {output_dir}")
    
    def generate_output_path(self, input_file: str, output_dir: str, 
                           output_format: AudioFormat) -> str:
        """生成输出文件路径"""
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        return os.path.join(output_dir, f"{base_name}.{output_format.value}")
    
    def extract_metadata(self, file_path: str) -> AudioMetadata:
        """提取音频元数据（可被子类重写）"""
        return AudioMetadata()
    
    def write_metadata(self, output_file: str, metadata: AudioMetadata) -> None:
        """写入音频元数据（可被子类重写）"""
        try:
            from mutagen import File
            audio = File(output_file, easy=True)
            if audio is not None:
                if metadata.title:
                    audio['title'] = metadata.title
                if metadata.artist:
                    audio['artist'] = metadata.artist
                if metadata.album:
                    audio['album'] = metadata.album
                if metadata.genre:
                    audio['genre'] = metadata.genre
                if metadata.year:
                    audio['date'] = str(metadata.year)
                if metadata.track:
                    audio['tracknumber'] = str(metadata.track)
                audio.save()
                self.logger.info("音频元数据写入成功")
        except Exception as e:
            self.logger.warning(f"写入音频元数据失败: {str(e)}")
