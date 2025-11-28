"""
OGG/QMC格式转换器
QQ音乐加密格式转换
"""
import os
import sys
from pathlib import Path
from typing import Optional, Callable

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.base import AudioConverter, ConversionResult, AudioFormat, AudioMetadata
from core.exceptions import ConversionError


class OGGConverter(AudioConverter):
    """OGG/QMC格式转换器"""
    
    def __init__(self):
        super().__init__()
        # QQ音乐的解密映射表
        self.mask = bytes([
            0x77, 0x48, 0x32, 0x73, 0xDE, 0xF2, 0xC0, 0xC8,
            0x95, 0xEC, 0x30, 0xB2, 0x51, 0xC3, 0xE1, 0xA0,
            0x9E, 0xE6, 0x9D, 0xCF, 0xFA, 0x7F, 0x14, 0xD1,
            0xCE, 0xB8, 0xDC, 0xC3, 0x4A, 0x67, 0x93, 0xD6,
        ])
    
    @property
    def supported_input_formats(self) -> list[AudioFormat]:
        return [AudioFormat.OGG, AudioFormat.QMC, AudioFormat.QMC0, 
                AudioFormat.QMC3, AudioFormat.QMCFLAC]
    
    @property
    def supported_output_formats(self) -> list[AudioFormat]:
        return [AudioFormat.MP3]
    
    def convert(self, input_file: str, output_dir: str,
                output_format: AudioFormat = AudioFormat.MP3,
                progress_callback: Optional[Callable[[int], None]] = None) -> ConversionResult:
        """转换QMC文件"""
        try:
            # 验证输入
            self.validate_input(input_file)
            self.ensure_output_dir(output_dir)
            
            # 生成输出路径
            output_path = self.generate_output_path(input_file, output_dir, output_format)
            
            self.logger.info(f"开始转换QMC文件: {input_file} -> {output_path}")
            
            # 解密QMC文件
            success = self._decrypt_qmc_file(input_file, output_path, progress_callback)
            
            if success:
                self.logger.info(f"QMC文件转换成功: {output_path}")
                return ConversionResult(success=True, output_file=output_path)
            else:
                raise ConversionError("QMC文件转换失败")
                
        except Exception as e:
            error_msg = f"QMC转换失败: {str(e)}"
            self.logger.error(error_msg)
            return ConversionResult(success=False, error_message=error_msg)
    
    def _decrypt_qmc_file(self, input_file: str, output_file: str,
                         progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """解密QMC文件"""
        try:
            # 读取加密文件
            with open(input_file, 'rb') as f:
                data = f.read()
            
            if progress_callback:
                progress_callback(25)
            
            # 解密数据
            decrypted = bytearray()
            total_bytes = len(data)
            
            for i, byte in enumerate(data):
                j = i & 0x1F
                decrypted.append(byte ^ self.mask[j])
                
                # 更新进度
                if progress_callback and i % 10000 == 0:
                    progress = 25 + int(i * 50 / total_bytes)
                    progress_callback(progress)
            
            if progress_callback:
                progress_callback(75)
            
            # 保存解密后的文件
            with open(output_file, 'wb') as f:
                f.write(decrypted)
            
            if progress_callback:
                progress_callback(100)
            
            return True
            
        except Exception as e:
            self.logger.error(f"QMC解密过程出错: {str(e)}")
            return False