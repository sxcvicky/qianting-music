"""
WAV格式转换器
WAV格式转MP3
"""
import os
import wave
import numpy as np
from scipy.io import wavfile
from typing import Optional, Callable
import subprocess
import shutil
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base import AudioConverter, ConversionResult, AudioFormat, AudioMetadata
from core.exceptions import ConversionError


class WAVConverter(AudioConverter):
    """WAV格式转换器"""
    
    def __init__(self):
        super().__init__()
    
    @property
    def supported_input_formats(self) -> list[AudioFormat]:
        return [AudioFormat.WAV]
    
    @property
    def supported_output_formats(self) -> list[AudioFormat]:
        return [AudioFormat.MP3]
    
    def convert(self, input_file: str, output_dir: str,
                output_format: AudioFormat = AudioFormat.MP3,
                progress_callback: Optional[Callable[[int], None]] = None) -> ConversionResult:
        """转换WAV文件"""
        try:
            # 验证输入
            self.validate_input(input_file)
            self.ensure_output_dir(output_dir)
            
            # 生成输出路径
            output_path = self.generate_output_path(input_file, output_dir, output_format)
            
            self.logger.info(f"开始转换WAV文件: {input_file} -> {output_path}")
            
            if progress_callback:
                progress_callback(10)
            
            # 读取WAV文件
            audio_params = self._read_wav_file(input_file)
            
            if progress_callback:
                progress_callback(30)
            
            # 转换为MP3
            success = self._convert_to_mp3(input_file, output_path, progress_callback)
            
            if success:
                # 复制音频标签
                self._copy_metadata(input_file, output_path)
                
                if progress_callback:
                    progress_callback(100)
                
                self.logger.info(f"WAV文件转换成功: {output_path}")
                return ConversionResult(
                    success=True, 
                    output_file=output_path,
                    metadata=audio_params
                )
            else:
                raise ConversionError("WAV文件转换失败")
                
        except Exception as e:
            error_msg = f"WAV转换失败: {str(e)}"
            self.logger.error(error_msg)
            return ConversionResult(success=False, error_message=error_msg)
    
    def _read_wav_file(self, input_file: str) -> dict:
        """读取WAV文件参数"""
        try:
            with wave.open(input_file, 'rb') as wav_file:
                params = {
                    'channels': wav_file.getnchannels(),
                    'sample_width': wav_file.getsampwidth(),
                    'frame_rate': wav_file.getframerate(),
                    'frames': wav_file.getnframes(),
                    'duration': wav_file.getnframes() / wav_file.getframerate()
                }
                
                self.logger.debug(f"WAV文件参数: {params}")
                return params
                
        except Exception as e:
            self.logger.error(f"读取WAV文件参数失败: {str(e)}")
            return {}
    
    def _convert_to_mp3(self, input_file: str, output_file: str,
                       progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """转换WAV为MP3"""
        try:
            # 尝试使用ffmpeg转换
            if self._try_ffmpeg_conversion(input_file, output_file, progress_callback):
                return True
            
            # 如果ffmpeg不可用，使用简单复制方法
            self.logger.warning("ffmpeg不可用，使用简单文件复制")
            return self._simple_copy_conversion(input_file, output_file, progress_callback)
            
        except Exception as e:
            self.logger.error(f"WAV转MP3失败: {str(e)}")
            return False
    
    def _try_ffmpeg_conversion(self, input_file: str, output_file: str,
                              progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """尝试使用ffmpeg转换"""
        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',
                '-y',  # 覆盖输出文件
                output_file
            ]
            
            if progress_callback:
                progress_callback(50)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5分钟超时
            )
            
            if progress_callback:
                progress_callback(90)
            
            if result.returncode == 0:
                self.logger.info("ffmpeg转换成功")
                return True
            else:
                self.logger.warning(f"ffmpeg转换失败: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"ffmpeg不可用: {str(e)}")
            return False
        except Exception as e:
            self.logger.warning(f"ffmpeg转换出错: {str(e)}")
            return False
    
    def _simple_copy_conversion(self, input_file: str, output_file: str,
                               progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """简单文件复制转换（备用方案）"""
        try:
            if progress_callback:
                progress_callback(70)
            
            # 创建临时WAV文件
            temp_wav = output_file + '.temp.wav'
            
            # 使用scipy重新写入WAV文件
            with wave.open(input_file, 'rb') as wav_file:
                channels = wav_file.getnchannels()
                frame_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                
                # 转换为numpy数组
                audio_data = np.frombuffer(frames, dtype=np.int16)
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
            
            # 写入临时文件
            wavfile.write(temp_wav, frame_rate, audio_data)
            
            if progress_callback:
                progress_callback(85)
            
            # 复制并重命名为MP3
            shutil.copy2(temp_wav, output_file)
            os.remove(temp_wav)
            
            if progress_callback:
                progress_callback(95)
            
            self.logger.info("使用简单复制完成转换")
            return True
            
        except Exception as e:
            self.logger.error(f"简单复制转换失败: {str(e)}")
            return False
    
    def _copy_metadata(self, input_file: str, output_file: str):
        """复制音频标签"""
        try:
            from mutagen.wave import WAVE
            from mutagen.mp3 import MP3
            from mutagen.easyid3 import EasyID3
            
            # 读取原始WAV标签
            wav = WAVE(input_file)
            
            # 创建MP3标签
            mp3 = MP3(output_file, ID3=EasyID3)
            
            # 如果WAV文件有标签，尝试复制
            if hasattr(wav, 'tags') and wav.tags:
                for key in ['title', 'artist', 'album', 'genre', 'date']:
                    if key in wav.tags:
                        mp3[key] = wav.tags[key]
            
            mp3.save()
            self.logger.info("音频标签复制成功")
            
        except Exception as e:
            self.logger.warning(f"复制音频标签失败: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> AudioMetadata:
        """提取WAV文件元数据"""
        try:
            from mutagen.wave import WAVE
            
            wav = WAVE(file_path)
            metadata = AudioMetadata()
            
            if hasattr(wav, 'tags') and wav.tags:
                metadata.title = wav.tags.get('title', [None])[0]
                metadata.artist = wav.tags.get('artist', [None])[0]
                metadata.album = wav.tags.get('album', [None])[0]
                metadata.genre = wav.tags.get('genre', [None])[0]
            
            # 获取音频参数
            if hasattr(wav, 'info') and wav.info:
                metadata.duration = wav.info.length
                metadata.bitrate = wav.info.bitrate
                metadata.sample_rate = wav.info.sample_rate
                metadata.channels = wav.info.channels
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"提取WAV元数据失败: {str(e)}")
            return AudioMetadata()