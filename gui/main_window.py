"""
主窗口模块
重构后的主界面
"""
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QListWidget, 
                            QTabWidget, QProgressBar, QMessageBox, QFrame, 
                            QTextEdit, QGroupBox, QGridLayout, QApplication, QDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.factory import ConverterFactory
from core.registry import register_all_converters, get_converter_info
from config import load_settings, save_settings
from gui.workers import ConversionWorker, BatchConversionWorker
from gui.dialogs import AboutDialog, SettingsDialog
from gui.single_conversion_tab import SingleConversionTab
from gui.styles import Styles
from gui.batch_conversion_tab import BatchConversionTab

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心组件
        self._init_core()
        
        # 加载设置
        self.settings = load_settings()
        
        # 初始化界面
        self._init_ui()
        self._apply_settings()
        self._setup_connections()
        
        # 初始化状态
        # 中文注释：初始化当前转换线程引用，避免关闭时访问不存在导致异常
        self.current_worker = None

        logger.info("主窗口初始化完成")
    
    def _init_core(self):
        """初始化核心组件"""
        try:
            # 注册所有转换器
            register_all_converters()
            
            # 获取转换器信息
            converter_info = get_converter_info()
            logger.info(f"转换器初始化完成: {converter_info}")
            
        except Exception as e:
            logger.error(f"核心组件初始化失败: {str(e)}")
            QMessageBox.critical(None, "初始化错误", f"程序初始化失败：{str(e)}")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("浅听音乐格式转换器 - 重构版")
        self.setMinimumSize(900, 700)
        
        # 设置应用图标
        self._set_app_icon()
        
        # 启用拖放
        self.setAcceptDrops(True)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(15)
        
        # 创建工具栏
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # 创建标签页
        tab_widget = self._create_tab_widget()
        main_layout.addWidget(tab_widget)
        
        # 创建状态栏
        self._create_status_bar()
        
        # 应用样式
        self.setStyleSheet(Styles.get_stylesheet())

    
    def _set_app_icon(self):
        """设置应用图标"""
        icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 应用标题
        title_label = QLabel("浅听音乐格式转换器")
        title_label.setObjectName("app_title")
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # 设置按钮
        settings_btn = QPushButton("设置")
        settings_btn.setObjectName("toolbar_btn")
        settings_btn.clicked.connect(self._show_settings)
        toolbar_layout.addWidget(settings_btn)
        
        # 关于按钮
        about_btn = QPushButton("关于")
        about_btn.setObjectName("toolbar_btn")
        about_btn.clicked.connect(self._show_about)
        toolbar_layout.addWidget(about_btn)
        
        return toolbar
    
    def _create_tab_widget(self) -> QTabWidget:
        """创建标签页组件"""
        tab_widget = QTabWidget()
        
        # 单文件转换页
        single_tab = self._create_single_conversion_tab()
        tab_widget.addTab(single_tab, "单文件转换")
        
        # 批量转换页
        self.batch_conversion_tab = BatchConversionTab(settings=self.settings, parent=self)
        tab_widget.addTab(self.batch_conversion_tab, "批量转换")
        

        
        # 系统信息页
        info_tab = self._create_info_tab()
        tab_widget.addTab(info_tab, "系统信息")
        
        return tab_widget
    
    def _create_single_conversion_tab(self) -> QWidget:
        """创建单文件转换标签页"""
        self.single_conversion_tab = SingleConversionTab(parent=self, settings=self.settings)
        self.single_conversion_tab.update_format_info(self._get_format_info_text())
        self.single_conversion_tab.select_output_btn.clicked.connect(self.single_conversion_tab._select_output_dir)
        return self.single_conversion_tab
    

    
    
    def _create_info_tab(self) -> QWidget:
        """创建系统信息标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 系统信息显示
        info_group = QGroupBox("系统信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(400)
        
        # 更新系统信息
        self._update_system_info()
        
        info_layout.addWidget(self.info_text)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新信息")
        refresh_btn.clicked.connect(self._update_system_info)
        info_layout.addWidget(refresh_btn)
        
        layout.addWidget(info_group)
        
        return widget
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = self.statusBar()
        status_bar.showMessage("就绪")
    
    def _get_format_info_text(self) -> str:
        """获取格式信息文本"""
        try:
            converter_info = get_converter_info()
            formats = converter_info.get('supported_formats', [])
            
            format_desc = {
                'kgm': 'KGM (酷狗音乐)',
                'ncm': 'NCM (网易云音乐)', 
                'ogg': 'OGG/QMC (QQ音乐)',
                'qmc': 'QMC (QQ音乐)',
                'qmc0': 'QMC0 (QQ音乐)',
                'qmc3': 'QMC3 (QQ音乐)',
                'qmcflac': 'QMCFLAC (QQ音乐)',
                'wav': 'WAV (无损音频)'
            }
            
            supported = []
            for fmt in formats:
                desc = format_desc.get(fmt, fmt.upper())
                supported.append(f"• {desc}")
            
            return f"支持的输入格式:\n" + "\n".join(supported) + "\n\n输出格式: MP3, FLAC"
            
        except Exception as e:
            logger.error(f"获取格式信息失败: {str(e)}")
            return "格式信息加载失败"
    
    def _apply_settings(self):
        """应用设置"""
        # 应用窗口大小
        if self.settings.window_width > 0 and self.settings.window_height > 0:
            self.resize(self.settings.window_width, self.settings.window_height)
        
        # 应用窗口位置
        if self.settings.window_x >= 0 and self.settings.window_y >= 0:
            self.move(self.settings.window_x, self.settings.window_y)
        
        # 更新输出目录标签
        if hasattr(self, 'single_conversion_tab'):
            self.single_conversion_tab.update_output_dir_label(self.settings.default_output_dir)
        if hasattr(self, 'batch_conversion_tab'):
            self.batch_conversion_tab.update_output_dir_label(self.settings.default_output_dir)
    
    def _setup_connections(self):
        """设置信号连接"""
        self.single_conversion_tab.select_file_btn.clicked.connect(self._select_input_file)
        self.single_conversion_tab.select_output_btn.clicked.connect(self.single_conversion_tab._select_output_dir)
        self.single_conversion_tab.convert_btn.clicked.connect(self._start_single_conversion)

    

    
    # 事件处理方法
    def _select_input_file(self):
        """选择输入文件"""
        try:
            # 移除 .mflac 扩展名（MFLAC 支持已下线）
            file_filter = "音频文件 (*.kgm *.ncm *.ogg *.qmc *.qmc0 *.qmc3 *.qmcflac *.wav);;所有文件 (*.*)"
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "选择音频文件", 
                self.settings.last_input_dir,
                file_filter
            )
            
            if file_path:
                self.single_conversion_tab.set_input_file_label(file_path)
                self.settings.last_input_dir = os.path.dirname(file_path)
                self.single_conversion_tab._check_convert_ready()

                
        except Exception as e:
            logger.error(f"选择文件时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"选择文件时出错：{str(e)}")
    

    

    
    def _start_single_conversion(self):
        """开始单文件转换"""
        input_file = self.single_conversion_tab.get_input_file_path()
        output_dir = self.single_conversion_tab.get_output_dir_path()
        
        if not input_file or input_file == "请选择要转换的文件":
            QMessageBox.warning(self, "警告", "请先选择要转换的文件！")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录！")
            return
        
        self.single_conversion_tab.enable_convert_button(False)
        self.single_conversion_tab.set_progress_bar_value(0)
        self.single_conversion_tab.set_status_label("正在转换...")
        
        logger.info(f"开始转换文件: {input_file} 到 {output_dir}")
        
        self.current_worker = ConversionWorker(input_file, output_dir, self)
        self.current_worker.progress.connect(self.single_conversion_tab._on_conversion_progress)
        self.current_worker.finished.connect(self.single_conversion_tab._single_conversion_finished)
        self.current_worker.error.connect(self.single_conversion_tab._on_conversion_error)
        self.current_worker.start()
    

    
    def _update_system_info(self):
        """更新系统信息"""
        try:
            import platform
            import sys
            from datetime import datetime
            
            info_text = f"""
系统信息 (更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
{"=" * 60}

操作系统: {platform.system()} {platform.release()}
Python版本: {sys.version}
PyQt6版本: {QApplication.applicationVersion()}

转换器信息:
{"=" * 30}
            """
            
            # 添加转换器信息
            converter_info = get_converter_info()
            info_text += f"""
支持格式数量: {len(converter_info.get('supported_formats', []))}
支持的格式: {', '.join(converter_info.get('supported_formats', []))}

转换器映射:
            """
            
            for format_name, converter_class in converter_info.get('format_mapping', {}).items():
                info_text += f"  {format_name.upper()}: {converter_class}\n"
            
            # 添加路径信息
            info_text += f"""

路径信息:
{"=" * 30}
当前工作目录: {os.getcwd()}
默认输出目录: {self.settings.default_output_dir}
上次输入目录: {self.settings.last_input_dir}
上次输出目录: {self.settings.last_output_dir}
            """
            
            # 添加配置信息
            info_text += f"""

配置信息:
{"=" * 30}
音频质量: {self.settings.audio_quality}
默认输出格式: {self.settings.default_output_format}
保留元数据: {self.settings.preserve_metadata}
覆盖已存在文件: {self.settings.overwrite_existing}
最大并发转换数: {self.settings.max_concurrent_conversions}
数据块大小: {self.settings.chunk_size_mb}MB
调试模式: {self.settings.enable_debug_mode}
            """
            
            self.info_text.setPlainText(info_text)
            
        except Exception as e:
            error_msg = f"获取系统信息失败: {str(e)}"
            logger.error(error_msg)
            self.info_text.setPlainText(error_msg)
    

    
    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新加载设置
            self.settings = load_settings()
            self._apply_settings()
            self._update_system_info()
            QMessageBox.information(self, "提示", "设置已应用")
    
    def _show_about(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    # 拖放事件处理
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖放进入事件"""
        if event.mimeData().hasUrls():
            # 检查文件格式
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if ConverterFactory.is_supported(file_path):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """处理文件拖放事件"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        supported_files = [f for f in files if ConverterFactory.is_supported(f)]
        
        if not supported_files:
            QMessageBox.warning(self, "警告", "没有发现支持的文件格式")
            return
        
        if len(supported_files) == 1:
            # 单个文件，设置到单文件转换页
            self.single_conversion_tab.set_input_file_label(supported_files[0])

        else:
            # 多个文件，添加到批量转换列表
            self.batch_conversion_tab.add_files(supported_files)
            
            # 切换到批量转换页
            tab_widget = self.centralWidget().findChild(QTabWidget)
            if tab_widget:
                tab_widget.setCurrentIndex(1)  # 批量转换页
        
        event.acceptProposedAction()
    
    # 窗口事件
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口位置和大小
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.settings.window_x = self.x()
        self.settings.window_y = self.y()
        
        # 保存设置
        save_settings(self.settings)
        
        # 检查是否有正在进行的转换
        # 中文注释：安全访问 current_worker，避免 AttributeError
        if getattr(self, "current_worker", None) is not None and not self.current_worker.isFinished():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "正在进行转换任务，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # 取消转换任务
            # 中文注释：请求取消当前转换线程并等待其结束
            self.current_worker.cancel()
            self.current_worker.wait(3000)  # 等待3秒
        
        logger.info("程序正常退出")
        event.accept()
