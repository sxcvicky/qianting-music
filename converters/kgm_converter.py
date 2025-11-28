"""
KGM格式转换器
酷狗音乐加密格式转换
"""
import os
import struct
import sys
from pathlib import Path
from typing import Optional, Callable

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base import AudioConverter, ConversionResult, AudioFormat, AudioMetadata
from core.exceptions import ConversionError, InvalidHeaderError


class KGMConverter(AudioConverter):
    """KGM格式转换器"""
    
    def __init__(self):
        super().__init__()
        # KGM文件的加密密钥
        self.key = [0x23, 0x31, 0x34, 0x6C, 0x6A, 0x6B, 0x5F, 0x21]
        # KGM文件头标识
        self.MAGIC = bytes([0x7c, 0xd5, 0x32, 0xeb])
        # 文件头长度
        self.HEADER_SIZE = 64
    
    @property
    def supported_input_formats(self) -> list[AudioFormat]:
        return [AudioFormat.KGM]
    
    @property
    def supported_output_formats(self) -> list[AudioFormat]:
        return [AudioFormat.MP3]
    
    def convert(self, input_file: str, output_dir: str,
                output_format: AudioFormat = AudioFormat.MP3,
                progress_callback: Optional[Callable[[int], None]] = None) -> ConversionResult:
        """转换KGM文件"""
        try:
            # 验证输入
            self.validate_input(input_file)
            self.ensure_output_dir(output_dir)
            
            # 生成输出路径
            output_path = self.generate_output_path(input_file, output_dir, output_format)
            
            self.logger.info(f"开始转换KGM文件: {input_file} -> {output_path}")
            
            # 解密KGM文件
            success = self._decrypt_kgm_file(input_file, output_path, progress_callback)
            
            if success and os.path.exists(output_path):
                self.logger.info(f"KGM文件转换成功: {output_path}")
                return ConversionResult(success=True, output_file=output_path)
            else:
                raise ConversionError("KGM文件转换失败，输出文件未生成")
                
        except Exception as e:
            error_msg = f"KGM转换失败: {str(e)}"
            self.logger.error(error_msg)
            return ConversionResult(success=False, error_message=error_msg)
    
    def _decrypt_kgm_file(self, input_file: str, output_file: str,
                         progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """解密KGM文件"""
        try:
            with open(input_file, 'rb') as f_in:
                # 验证文件头
                if not self._verify_header(f_in):
                    raise InvalidHeaderError(f"不是有效的KGM文件: {input_file}")
                
                # 读取文件信息
                file_info = self._read_file_info(f_in)
                if not file_info:
                    raise ConversionError(f"无法读取KGM文件信息: {input_file}")
                
                self.logger.debug(f"KGM文件信息: {file_info}")
                
                # 解密并写入数据
                with open(output_file, 'wb') as f_out:
                    total_size = os.path.getsize(input_file)
                    data_start = f_in.tell()
                    processed_size = data_start
                    
                    chunk_size = 1024
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        
                        # 解密数据
                        decrypted = self._decrypt_chunk(chunk)
                        f_out.write(decrypted)
                        
                        processed_size += len(chunk)
                        
                        # 更新进度
                        if progress_callback:
                            progress = int((processed_size - data_start) * 100 / (total_size - data_start))
                            progress_callback(min(100, progress))
            
            return True
            
        except Exception as e:
            self.logger.error(f"KGM解密过程出错: {str(e)}")
            return False
    
    def _verify_header(self, f) -> bool:
        """验证KGM文件头"""
        try:
            # 读取魔数(4字节)
            magic = f.read(4)
            if magic != self.MAGIC:
                self.logger.error(f"无效的文件头魔数: {magic.hex()}")
                return False
            
            # 读取版本信息(4字节)
            version_info = f.read(4)
            self.logger.debug(f"版本信息: {version_info.hex()}")
            
            # 读取剩余头部信息
            header_data = f.read(self.HEADER_SIZE - 8)  # 减去已读的8字节
            self.logger.debug(f"头部信息: {header_data.hex()}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"验证文件头时出错: {str(e)}")
            return False
    
    def _read_file_info(self, f) -> dict:
        """读取KGM文件信息"""
        try:
            # KGM文件的数据部分直接从头部之后开始
            return {
                'data_offset': self.HEADER_SIZE,
                'header_size': self.HEADER_SIZE
            }
        except Exception as e:
            self.logger.error(f"读取文件信息时出错: {str(e)}")
            return None
    
    def _decrypt_chunk(self, data: bytes) -> bytes:
        """解密数据块"""
        result = bytearray()
        key_len = len(self.key)
        
        for i, byte in enumerate(data):
            # 使用密钥进行异或解密
            key_byte = self.key[i % key_len]
            decrypted_byte = byte ^ key_byte
            result.append(decrypted_byte)
        
        return bytes(result)
    
    def analyze_file(self, input_file: str) -> dict:
        """分析KGM文件结构"""
        try:
            with open(input_file, 'rb') as f:
                # 读取前64字节进行分析
                header_data = f.read(64)
                
                analysis = {
                    'file_path': input_file,
                    'file_size': os.path.getsize(input_file),
                    'header_hex': ' '.join(f'{b:02x}' for b in header_data),
                    'header_ascii': ''.join(chr(b) if 32 <= b <= 126 else '.' for b in header_data),
                    'magic_valid': header_data[:4] == self.MAGIC
                }
                
                self.logger.info(f"KGM文件分析结果: {analysis}")
                return analysis
                
        except Exception as e:
            self.logger.error(f"分析KGM文件时出错: {str(e)}")
            return {}