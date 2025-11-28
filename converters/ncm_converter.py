"""
NCM格式转换器
网易云音乐加密格式转换
"""
import binascii
import struct
import base64
import json
import os
import sys
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from typing import Optional, Callable, Dict, Any

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base import AudioConverter, ConversionResult, AudioFormat, AudioMetadata
from core.exceptions import ConversionError, InvalidHeaderError, DecryptionError


class NCMConverter(AudioConverter):
    """NCM格式转换器"""
    
    def __init__(self):
        super().__init__()
        self.core_key = binascii.a2b_hex('687A4852416D736F356B496E62617857')
        self.meta_key = binascii.a2b_hex('2331346C6A6B5F215C5D2630553C2728')
    
    @property
    def supported_input_formats(self) -> list[AudioFormat]:
        return [AudioFormat.NCM]
    
    @property 
    def supported_output_formats(self) -> list[AudioFormat]:
        return [AudioFormat.MP3, AudioFormat.FLAC]
    
    def convert(self, input_file: str, output_dir: str,
                output_format: AudioFormat = AudioFormat.MP3,
                progress_callback: Optional[Callable[[int], None]] = None) -> ConversionResult:
        """转换NCM文件"""
        try:
            # 验证输入
            self.validate_input(input_file)
            self.ensure_output_dir(output_dir)
            
            self.logger.info(f"开始转换NCM文件: {input_file}")
            
            # 解密NCM文件
            audio_data, key_data, meta_data = self._decrypt_ncm_file(input_file, progress_callback)
            
            # 根据元数据确定输出格式
            detected_format = meta_data.get('format', 'mp3')
            if detected_format in ['flac']:
                output_format = AudioFormat.FLAC
            else:
                output_format = AudioFormat.MP3
            
            # 生成输出路径
            output_path = self.generate_output_path(input_file, output_dir, output_format)
            
            # 写入解密后的音频文件
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            self.logger.info(f"音频文件写入完成: {output_path}")
            
            # 写入元数据
            if meta_data:
                metadata = self._convert_metadata(meta_data)
                self.write_metadata(output_path, metadata)
            
            return ConversionResult(
                success=True,
                output_file=output_path,
                metadata=meta_data
            )
            
        except Exception as e:
            error_msg = f"NCM转换失败: {str(e)}"
            self.logger.error(error_msg)
            return ConversionResult(success=False, error_message=error_msg)
    
    def _decrypt_ncm_file(self, file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> tuple:
        """解密NCM文件并返回音频数据、密钥数据和元数据"""
        try:
            with open(file_path, 'rb') as f:
                total_size = os.path.getsize(file_path)
                
                # 检查文件头
                header = f.read(8)
                if header != b'CTENFDAM':
                    raise InvalidHeaderError(f"不是有效的NCM文件，文件头: {header}")
                
                f.seek(2, 1)
                
                # 读取密钥长度和数据
                key_length = struct.unpack('<I', f.read(4))[0]
                key_data = self._decrypt_key_data(f.read(key_length))
                
                # 读取元数据
                meta_length = struct.unpack('<I', f.read(4))[0] 
                meta_data = self._decrypt_metadata(f, meta_length) if meta_length else {}
                
                # 跳过CRC校验
                f.seek(9, 1)
                
                # 读取音频数据
                audio_data = f.read()
                
                if progress_callback:
                    progress_callback(50)
                
                # 解密音频内容
                decrypted_audio = self._decrypt_audio_content(audio_data, key_data, progress_callback)
                
                if progress_callback:
                    progress_callback(100)
                
                return decrypted_audio, key_data, meta_data
                
        except Exception as e:
            raise ConversionError(f"NCM文件解密失败: {str(e)}")
    
    def _decrypt_key_data(self, key_data: bytes) -> bytes:
        """解密密钥数据"""
        key_data_array = bytearray(key_data)
        for i in range(len(key_data_array)):
            key_data_array[i] ^= 0x64
        
        cryptor = AES.new(self.core_key, AES.MODE_ECB)
        key_data = cryptor.decrypt(bytes(key_data_array))
        
        # 移除AES填充
        while key_data[-1] == key_data[-2] == key_data[-3] == key_data[-4]:
            key_data = key_data[:-key_data[-1]]
        
        key_data = key_data[17:]
        key_data_array = bytearray(key_data)
        for i in range(len(key_data_array)):
            key_data_array[i] ^= 0x63
        
        return bytes(key_data_array)
    
    def _decrypt_metadata(self, f, meta_length: int) -> Dict[str, Any]:
        """解密元数据"""
        if meta_length == 0:
            return {}
        
        try:
            meta_data_array = bytearray(f.read(meta_length))
            for i in range(len(meta_data_array)):
                meta_data_array[i] ^= 0x63
            
            cryptor = AES.new(self.meta_key, AES.MODE_ECB)
            meta_data = cryptor.decrypt(bytes(meta_data_array))
            
            # 移除AES填充
            while meta_data[-1] == meta_data[-2] == meta_data[-3] == meta_data[-4]:
                meta_data = meta_data[:-meta_data[-1]]
            
            meta_data = meta_data[22:].decode('utf-8')
            return json.loads(meta_data)
            
        except Exception as e:
            self.logger.warning(f"解析元数据失败: {e}")
            return {}
    
    def _decrypt_audio_content(self, audio_data: bytes, key_data: bytes, 
                             progress_callback: Optional[Callable[[int], None]] = None) -> bytes:
        """解密音频内容"""
        key_length = len(key_data)
        key_box = bytearray(range(256))
        c = 0
        last_byte = 0
        key_offset = 0
        
        # 初始化密钥盒
        for i in range(256):
            swap = key_box[i]
            c = (swap + last_byte + key_data[key_offset]) & 0xff
            key_offset += 1
            if key_offset >= key_length:
                key_offset = 0
            key_box[i] = key_box[c]
            key_box[c] = swap
            last_byte = c
        
        # 解密音频数据
        key_box_array = bytearray(key_box)
        audio_data_array = bytearray(audio_data)
        
        c = 0
        last_byte = 0
        
        total_bytes = len(audio_data_array)
        for i in range(total_bytes):
            c = (c + 1) & 0xff
            swap = key_box_array[c]
            last_byte = (last_byte + swap) & 0xff
            key_box_array[c] = key_box_array[last_byte]
            key_box_array[last_byte] = swap
            key_offset = (key_box_array[c] + key_box_array[last_byte]) & 0xff
            audio_data_array[i] ^= key_box_array[key_offset]
            
            # 更新进度
            if progress_callback and i % 10000 == 0:
                progress = 50 + int(i * 50 / total_bytes)
                progress_callback(progress)
        
        return bytes(audio_data_array)
    
    def _convert_metadata(self, meta_data: Dict[str, Any]) -> AudioMetadata:
        """转换元数据格式"""
        return AudioMetadata(
            title=meta_data.get('musicName'),
            artist=meta_data.get('artist'),
            album=meta_data.get('album'),
            genre=meta_data.get('genre'),
            year=meta_data.get('publishTime'),
            track=meta_data.get('trackNumber'),
            duration=meta_data.get('duration'),
            bitrate=meta_data.get('bitrate')
        )