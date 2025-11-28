"""
工作线程模块
处理音频转换的后台任务
"""
import logging
import sys
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core import ConverterFactory, ConversionResult

logger = logging.getLogger(__name__)


class ConversionWorker(QThread):
    """通用转换工作线程"""
    
    # 信号定义
    finished = pyqtSignal(ConversionResult)  # 转换完成
    progress = pyqtSignal(int)  # 进度更新
    error = pyqtSignal(str)  # 错误信息
    status_changed = pyqtSignal(str)  # 状态变化
    
    def __init__(self, input_file: str, output_dir: str, parent=None):
        super().__init__(parent)
        self.input_file = input_file
        self.output_dir = output_dir
        self._converter = None
        self._is_cancelled = False
    
    def run(self):
        """执行转换任务"""
        try:
            self.status_changed.emit("初始化转换器...")
            
            # 创建转换器
            self._converter = ConverterFactory.create_converter(self.input_file)
            
            # 检查是否被取消
            if self._is_cancelled:
                return
            
            self.status_changed.emit("开始转换...")
            logger.info(f"开始转换: {self.input_file}")
            
            # 执行转换
            result = self._converter.convert(
                input_file=self.input_file,
                output_dir=self.output_dir,
                progress_callback=self._on_progress
            )
            
            # 检查是否被取消
            if self._is_cancelled:
                return
            
            if result.success:
                self.status_changed.emit("转换完成")
                logger.info(f"转换成功: {result.output_file}")
            else:
                self.status_changed.emit("转换失败")
                logger.error(f"转换失败: {result.error_message}")
            
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"转换过程出错: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    def _on_progress(self, progress: int):
        """进度回调"""
        if not self._is_cancelled:
            self.progress.emit(progress)
    
    def cancel(self):
        """取消转换"""
        self._is_cancelled = True
        self.status_changed.emit("正在取消...")
        logger.info("用户取消了转换任务")
    
    @property
    def is_cancelled(self) -> bool:
        """是否已取消"""
        return self._is_cancelled


class BatchConversionWorker(QThread):
    """批量转换工作线程"""
    
    # 信号定义
    file_started = pyqtSignal(str)  # 开始处理文件
    file_finished = pyqtSignal(str, ConversionResult)  # 文件处理完成
    progress = pyqtSignal(int, int)  # 进度更新 (当前文件进度, 总体进度)
    all_finished = pyqtSignal(list)  # 全部完成
    error = pyqtSignal(str)  # 错误信息
    status_changed = pyqtSignal(str)  # 状态变化
    
    def __init__(self, input_files: list[str], output_dir: str, parent=None):
        super().__init__(parent)
        self.input_files = input_files
        self.output_dir = output_dir
        self._is_cancelled = False
        self._results = []
    
    def run(self):
        """执行批量转换"""
        try:
            total_files = len(self.input_files)
            self._results = []
            
            for i, input_file in enumerate(self.input_files):
                if self._is_cancelled:
                    break
                
                self.file_started.emit(input_file)
                self.status_changed.emit(f"转换文件 {i+1}/{total_files}: {input_file}")
                
                try:
                    # 创建转换器
                    converter = ConverterFactory.create_converter(input_file)
                    
                    # 执行转换
                    result = converter.convert(
                        input_file=input_file,
                        output_dir=self.output_dir,
                        progress_callback=lambda p: self._on_file_progress(p, i, total_files)
                    )
                    
                    self._results.append((input_file, result))
                    self.file_finished.emit(input_file, result)
                    
                except Exception as e:
                    error_result = ConversionResult(success=False, error_message=str(e))
                    self._results.append((input_file, error_result))
                    self.file_finished.emit(input_file, error_result)
                
                # 更新总体进度
                overall_progress = int((i + 1) * 100 / total_files)
                self.progress.emit(100, overall_progress)
            
            if not self._is_cancelled:
                self.status_changed.emit("批量转换完成")
                self.all_finished.emit(self._results)
            
        except Exception as e:
            error_msg = f"批量转换过程出错: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
    
    def _on_file_progress(self, file_progress: int, file_index: int, total_files: int):
        """文件进度回调"""
        if not self._is_cancelled:
            # 计算总体进度
            overall_progress = int((file_index * 100 + file_progress) / total_files)
            self.progress.emit(file_progress, overall_progress)
    
    def cancel(self):
        """取消批量转换"""
        self._is_cancelled = True
        self.status_changed.emit("正在取消批量转换...")
        logger.info("用户取消了批量转换任务")
    
    @property
    def is_cancelled(self) -> bool:
        """是否已取消"""
        return self._is_cancelled