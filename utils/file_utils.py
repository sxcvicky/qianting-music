"""
文件工具模块
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class FileValidator:
    """文件验证器"""
    
    SUPPORTED_EXTENSIONS = {
        # 支持的输入/输出扩展名列表（移除 .mflac）
        '.kgm', '.ncm', '.ogg', '.qmc', '.qmc0', '.qmc3',
        '.qmcflac', '.wav', '.mp3', '.flac'
    }
    
    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """检查是否为支持的文件格式"""
        ext = Path(file_path).suffix.lower()
        return ext in FileValidator.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """验证文件路径"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, "文件不存在"
            
            if not path.is_file():
                return False, "路径不是文件"
            
            if not os.access(file_path, os.R_OK):
                return False, "文件不可读"
            
            if path.stat().st_size == 0:
                return False, "文件为空"
            
            if not FileValidator.is_supported_file(file_path):
                return False, "不支持的文件格式"
            
            return True, "文件验证通过"
            
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"
    
    @staticmethod
    def validate_directory(dir_path: str, create_if_not_exist: bool = True) -> Tuple[bool, str]:
        """验证目录路径"""
        try:
            path = Path(dir_path)
            
            if not path.exists():
                if create_if_not_exist:
                    path.mkdir(parents=True, exist_ok=True)
                    return True, "目录创建成功"
                else:
                    return False, "目录不存在"
            
            if not path.is_dir():
                return False, "路径不是目录"
            
            if not os.access(dir_path, os.W_OK):
                return False, "目录不可写"
            
            return True, "目录验证通过"
            
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """获取安全的文件名"""
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_filename = filename
        
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # 移除首尾空格和点号
        safe_filename = safe_filename.strip(' .')
        
        # 确保不为空
        if not safe_filename:
            safe_filename = "untitled"
        
        return safe_filename


class PathManager:
    """路径管理器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
    
    def get_output_path(self, input_file: str, output_dir: str, 
                       output_format: str = "mp3") -> str:
        """生成输出文件路径"""
        input_path = Path(input_file)
        output_path = Path(output_dir)
        
        # 获取安全的文件名
        base_name = FileValidator.get_safe_filename(input_path.stem)
        output_filename = f"{base_name}.{output_format.lower()}"
        
        return str(output_path / output_filename)
    
    def get_unique_path(self, file_path: str) -> str:
        """获取唯一的文件路径（避免重名）"""
        path = Path(file_path)
        
        if not path.exists():
            return str(path)
        
        # 生成唯一文件名
        counter = 1
        while True:
            stem = path.stem
            suffix = path.suffix
            parent = path.parent
            
            new_name = f"{stem}_{counter:03d}{suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return str(new_path)
            
            counter += 1
            
            # 防止无限循环
            if counter > 999:
                raise ValueError("无法生成唯一文件名")
    
    def cleanup_temp_files(self, pattern: str = "*.temp") -> int:
        """清理临时文件"""
        try:
            temp_files = list(self.base_dir.glob(pattern))
            
            cleaned_count = 0
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"删除临时文件失败: {temp_file}, 错误: {str(e)}")
            
            logger.info(f"清理了 {cleaned_count} 个临时文件")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理临时文件失败: {str(e)}")
            return 0
    
    def get_disk_usage(self, path: str) -> dict:
        """获取磁盘使用情况"""
        try:
            total, used, free = shutil.disk_usage(path)
            
            return {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'usage_percent': round(used / total * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"获取磁盘使用情况失败: {str(e)}")
            return {}
    
    def ensure_directory_structure(self, directories: List[str]) -> bool:
        """确保目录结构存在"""
        try:
            for dir_name in directories:
                dir_path = self.base_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"目录结构创建完成: {directories}")
            return True
            
        except Exception as e:
            logger.error(f"创建目录结构失败: {str(e)}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """获取文件详细信息"""
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'name': path.name,
                'stem': path.stem,
                'suffix': path.suffix,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024**2), 2),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'absolute_path': str(path.absolute())
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return {}
