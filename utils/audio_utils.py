"""
音频工具模块
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """音频文件分析器"""
    
    @staticmethod
    def analyze_file_header(file_path: str, max_bytes: int = 1024) -> Dict[str, Any]:
        """分析文件头部信息"""
        try:
            with open(file_path, 'rb') as f:
                header_data = f.read(max_bytes)
            
            analysis = {
                'file_size': os.path.getsize(file_path),
                'header_hex': header_data[:64].hex(),
                'header_ascii': ''.join(chr(b) if 32 <= b <= 126 else '.' for b in header_data[:64]),
                'magic_signatures': AudioAnalyzer._detect_magic_signatures(header_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析文件头失败: {str(e)}")
            return {}
    
    @staticmethod
    def _detect_magic_signatures(data: bytes) -> Dict[str, bool]:
        """检测魔数签名"""
        signatures = {
            'NCM': data.startswith(b'CTENFDAM'),
            'KGM': data.startswith(bytes([0x7c, 0xd5, 0x32, 0xeb])),
            'MP3': data.startswith(b'ID3') or data.startswith(b'\xff\xfb'),
            'FLAC': data.startswith(b'fLaC'),
            'WAV': data.startswith(b'RIFF') and b'WAVE' in data[:12],
            'OGG': data.startswith(b'OggS'),
        }
        
        return signatures
    
    @staticmethod
    def get_audio_format_info(file_path: str) -> Dict[str, Any]:
        """获取音频格式信息"""
        try:
            ext = Path(file_path).suffix.lower().lstrip('.')
            file_size = os.path.getsize(file_path)
            
            format_info = {
                'extension': ext,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                # 移除 mflac（新版不可转换）
                'is_encrypted': ext in ['ncm', 'kgm', 'qmc', 'qmc0', 'qmc3', 'qmcflac'],
                'estimated_duration': None  # 可以添加更复杂的分析逻辑
            }
            
            return format_info
            
        except Exception as e:
            logger.error(f"获取音频格式信息失败: {str(e)}")
            return {}


class AudioMetadataExtractor:
    """音频元数据提取器"""
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """提取音频元数据"""
        try:
            from mutagen import File
            
            audio_file = File(file_path)
            if audio_file is None:
                return {}
            
            metadata = {
                'title': None,
                'artist': None,
                'album': None,
                'genre': None,
                'year': None,
                'track': None,
                'duration': None,
                'bitrate': None,
                'sample_rate': None,
                'channels': None
            }
            
            # 提取基本信息
            if hasattr(audio_file, 'info') and audio_file.info:
                metadata.update({
                    'duration': getattr(audio_file.info, 'length', None),
                    'bitrate': getattr(audio_file.info, 'bitrate', None),
                    'sample_rate': getattr(audio_file.info, 'sample_rate', None),
                    'channels': getattr(audio_file.info, 'channels', None)
                })
            
            # 提取标签信息
            if hasattr(audio_file, 'tags') and audio_file.tags:
                tags = audio_file.tags
                
                # 尝试不同的标签格式
                tag_mappings = {
                    'title': ['TIT2', 'TITLE', '\xa9nam'],
                    'artist': ['TPE1', 'ARTIST', '\xa9ART'],
                    'album': ['TALB', 'ALBUM', '\xa9alb'],
                    'genre': ['TCON', 'GENRE', '\xa9gen'],
                    'year': ['TDRC', 'DATE', '\xa9day'],
                    'track': ['TRCK', 'TRACKNUMBER', 'trkn']
                }
                
                for field, possible_keys in tag_mappings.items():
                    for key in possible_keys:
                        if key in tags:
                            value = tags[key]
                            if isinstance(value, list) and value:
                                metadata[field] = str(value[0])
                            else:
                                metadata[field] = str(value)
                            break
            
            return metadata
            
        except Exception as e:
            logger.error(f"提取音频元数据失败: {str(e)}")
            return {}
    
    @staticmethod
    def write_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """写入音频元数据"""
        try:
            from mutagen import File
            from mutagen.easyid3 import EasyID3
            from mutagen.mp3 import MP3
            
            # 尝试加载文件
            audio_file = File(file_path, easy=True)
            
            # 如果是MP3文件但没有ID3标签，创建一个
            if file_path.lower().endswith('.mp3') and audio_file is None:
                audio_file = MP3(file_path, ID3=EasyID3)
            
            if audio_file is None:
                logger.warning(f"无法写入元数据到文件: {file_path}")
                return False
            
            # 写入元数据
            tag_mapping = {
                'title': 'title',
                'artist': 'artist', 
                'album': 'album',
                'genre': 'genre',
                'year': 'date',
                'track': 'tracknumber'
            }
            
            for field, tag in tag_mapping.items():
                if metadata.get(field):
                    audio_file[tag] = str(metadata[field])
            
            audio_file.save()
            logger.info(f"音频元数据写入成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"写入音频元数据失败: {str(e)}")
            return False
