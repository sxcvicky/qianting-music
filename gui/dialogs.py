"""
对话框模块
包含关于对话框和设置对话框
"""
import logging
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTabWidget,
                            QFormLayout, QLineEdit, QComboBox, QCheckBox,
                            QSpinBox, QGroupBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import AppSettings, load_settings, save_settings

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(450, 550)
        self.setModal(True)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll)
        
        # 创建滚动内容容器
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title = QLabel("超新星音频格式转换器")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 版本信息
        version = QLabel("版本：3.0.0 (重构版)")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # 功能特点
        features = QLabel("""
<h3>功能特点：</h3>
• 支持多种加密音频格式转换<br>
• 模块化架构，易于扩展<br>
• 统一的转换器接口<br>
• 智能格式识别<br>
• 批量转换支持<br>
• 进度显示和错误处理<br>
• 配置管理和持久化<br>
• 现代化的用户界面

<h3>支持格式：</h3>
• KGM (酷狗音乐) → MP3<br>
• NCM (网易云音乐) → MP3/FLAC<br>
• QMC/OGG (QQ音乐) → MP3<br>
• WAV → MP3<br>
<!-- MFLAC 已移除：新版不可转换，功能下线 -->

<h3>架构优势：</h3>
• 基于工厂模式的转换器管理<br>
• 抽象基类确保一致性<br>
• 配置管理系统<br>
• 模块化设计便于维护<br>
• 统一的错误处理机制
        """)
        features.setWordWrap(True)
        layout.addWidget(features)

        # 许可证信息（MIT）
        # 中文说明：明确项目采用 MIT 许可证，并提示用户可查看完整文本
        license_info = QLabel(
            """
<h3>许可证：</h3>
本项目采用 <b>MIT License</b> 开源许可证。<br>
该许可证允许自由使用、复制、修改和分发，但需保留版权与许可声明。<br>
完整文本请点击下方按钮查看。
            """
        )
        license_info.setWordWrap(True)
        layout.addWidget(license_info)

        # 免责声明
        disclaimer = QLabel("""
<h3 style="color: #FF5252;">免责声明：</h3>
本软件仅供个人学习研究使用，请勿用于商业用途。<br>
使用本软件转换的音频文件，仅供试听，请支持正版。<br>
<br>
<b>版权声明：</b><br>
1. 本软件是一个音频格式转换工具，仅提供格式转换功能<br>
2. 用户应确保拥有音频文件的合法使用权<br>
3. 不得将本软件用于任何非法用途<br>
4. 使用本软件所产生的任何法律责任由用户自行承担
        """)
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)
        
        # 联系方式
        contact = QLabel("""
<h3>联系方式：</h3>
作者：浅听音乐开发团队<br>
邮箱：447543475@qq.com<br>
项目架构：模块化重构版本
        """)
        contact.setWordWrap(True)
        layout.addWidget(contact)

        # 底部按钮区：查看许可证 / 访问 GitHub / 确定
        button_container = QWidget()
        btn_layout = QHBoxLayout(button_container)
        btn_layout.setContentsMargins(0, 15, 0, 0)

        # 中文说明：打开项目根目录的 LICENSE 文件
        license_btn = QPushButton("查看许可证")
        license_btn.setFixedSize(110, 35)
        license_btn.clicked.connect(self._open_license)

        # 中文说明：打开项目 GitHub 仓库页面
        github_btn = QPushButton("访问 GitHub 仓库")
        github_btn.setFixedSize(140, 35)
        github_btn.clicked.connect(self._open_github)

        ok_button = QPushButton("确定")
        ok_button.setFixedSize(100, 35)
        ok_button.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(license_btn)
        btn_layout.addWidget(github_btn)
        btn_layout.addWidget(ok_button)
        btn_layout.addStretch()

        main_layout.addWidget(button_container)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                line-height: 1.4;
            }
            QLabel#title {
                font-size: 20px;
                font-weight: bold;
                color: #1565C0;
                margin: 10px 0;
            }
            QLabel#version {
                font-size: 14px;
                color: #666666;
                margin-bottom: 20px;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        ")

    def _open_license(self):
        """打开项目根目录的 LICENSE 文件（中文说明）"""
        license_path = PROJECT_ROOT / "LICENSE"
        if license_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(license_path)))
        else:
            QMessageBox.warning(self, "未找到许可证文件", "在项目根目录未检测到 LICENSE 文件。")

    def _open_github(self):
        """打开 GitHub 仓库页面（中文说明）"""
        url = "https://github.com/sxcvicky/qianting-music"
        QDesktopServices.openUrl(QUrl(url))


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        self.settings = load_settings()
        self._setup_ui()
        self._load_current_settings()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 常规设置
        general_tab = self._create_general_tab()
        tab_widget.addTab(general_tab, "常规")
        
        # 转换设置
        conversion_tab = self._create_conversion_tab()
        tab_widget.addTab(conversion_tab, "转换")
        
        # 界面设置
        ui_tab = self._create_ui_tab()
        tab_widget.addTab(ui_tab, "界面")
        
        # 高级设置
        advanced_tab = self._create_advanced_tab()
        tab_widget.addTab(advanced_tab, "高级")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._reset_settings)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._save_and_accept)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """创建常规设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 路径设置组
        path_group = QGroupBox("路径设置")
        path_layout = QFormLayout(path_group)
        
        self.default_output_edit = QLineEdit()
        output_browse_btn = QPushButton("浏览...")
        output_browse_btn.clicked.connect(self._browse_output_dir)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.default_output_edit)
        output_layout.addWidget(output_browse_btn)
        
        path_layout.addRow("默认输出目录:", output_layout)
        
        layout.addWidget(path_group)
        
        # 行为设置组
        behavior_group = QGroupBox("行为设置")
        behavior_layout = QFormLayout(behavior_group)
        
        self.preserve_metadata_cb = QCheckBox("保留音频元数据")
        self.overwrite_existing_cb = QCheckBox("覆盖已存在的文件")
        self.auto_check_updates_cb = QCheckBox("自动检查更新")
        
        behavior_layout.addRow(self.preserve_metadata_cb)
        behavior_layout.addRow(self.overwrite_existing_cb)
        behavior_layout.addRow(self.auto_check_updates_cb)
        
        layout.addWidget(behavior_group)
        layout.addStretch()
        
        return widget
    
    def _create_conversion_tab(self) -> QWidget:
        """创建转换设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 转换设置组
        conversion_group = QGroupBox("转换设置")
        conversion_layout = QFormLayout(conversion_group)
        
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["mp3", "flac"])
        
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["low", "normal", "high"])
        
        conversion_layout.addRow("默认输出格式:", self.output_format_combo)
        conversion_layout.addRow("音频质量:", self.audio_quality_combo)
        
        layout.addWidget(conversion_group)
        
        # 性能设置组
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout(performance_group)
        
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setRange(1, 16)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(1, 100)
        self.chunk_size_spin.setSuffix(" MB")
        
        performance_layout.addRow("最大并发转换数:", self.max_concurrent_spin)
        performance_layout.addRow("数据块大小:", self.chunk_size_spin)
        
        layout.addWidget(performance_group)
        layout.addStretch()
        
        return widget
    
    def _create_ui_tab(self) -> QWidget:
        """创建界面设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout(ui_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["default", "dark", "light"])
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh_CN", "en_US"])
        
        ui_layout.addRow("主题:", self.theme_combo)
        ui_layout.addRow("语言:", self.language_combo)
        
        layout.addWidget(ui_group)
        
        # 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QFormLayout(window_group)
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(400, 3840)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(300, 2160)
        
        window_layout.addRow("窗口宽度:", self.window_width_spin)
        window_layout.addRow("窗口高度:", self.window_height_spin)
        
        layout.addWidget(window_group)
        layout.addStretch()
        
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """创建高级设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QFormLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        
        self.enable_file_logging_cb = QCheckBox("启用文件日志")
        
        self.max_log_files_spin = QSpinBox()
        self.max_log_files_spin.setRange(1, 100)
        
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 1000)
        self.max_log_size_spin.setSuffix(" MB")
        
        log_layout.addRow("日志级别:", self.log_level_combo)
        log_layout.addRow(self.enable_file_logging_cb)
        log_layout.addRow("最大日志文件数:", self.max_log_files_spin)
        log_layout.addRow("单个日志文件大小:", self.max_log_size_spin)
        
        layout.addWidget(log_group)
        
        # 调试设置组
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout(debug_group)
        
        self.enable_debug_cb = QCheckBox("启用调试模式")
        self.send_statistics_cb = QCheckBox("发送使用统计")
        
        debug_layout.addRow(self.enable_debug_cb)
        debug_layout.addRow(self.send_statistics_cb)
        
        layout.addWidget(debug_group)
        layout.addStretch()
        
        return widget
    
    def _load_current_settings(self):
        """加载当前设置到界面"""
        # 常规设置
        self.default_output_edit.setText(self.settings.default_output_dir)
        self.preserve_metadata_cb.setChecked(self.settings.preserve_metadata)
        self.overwrite_existing_cb.setChecked(self.settings.overwrite_existing)
        self.auto_check_updates_cb.setChecked(self.settings.auto_check_updates)
        
        # 转换设置
        self.output_format_combo.setCurrentText(self.settings.default_output_format)
        self.audio_quality_combo.setCurrentText(self.settings.audio_quality)
        self.max_concurrent_spin.setValue(self.settings.max_concurrent_conversions)
        self.chunk_size_spin.setValue(self.settings.chunk_size_mb)
        
        # 界面设置
        self.theme_combo.setCurrentText(self.settings.theme)
        self.language_combo.setCurrentText(self.settings.language)
        self.window_width_spin.setValue(self.settings.window_width)
        self.window_height_spin.setValue(self.settings.window_height)
        
        # 高级设置
        self.log_level_combo.setCurrentText(self.settings.log_level)
        self.enable_file_logging_cb.setChecked(self.settings.enable_file_logging)
        self.max_log_files_spin.setValue(self.settings.max_log_files)
        self.max_log_size_spin.setValue(self.settings.max_log_size_mb)
        self.enable_debug_cb.setChecked(self.settings.enable_debug_mode)
        self.send_statistics_cb.setChecked(self.settings.send_usage_statistics)
    
    def _save_current_settings(self):
        """保存当前界面设置"""
        # 常规设置
        self.settings.default_output_dir = self.default_output_edit.text()
        self.settings.preserve_metadata = self.preserve_metadata_cb.isChecked()
        self.settings.overwrite_existing = self.overwrite_existing_cb.isChecked()
        self.settings.auto_check_updates = self.auto_check_updates_cb.isChecked()
        
        # 转换设置
        self.settings.default_output_format = self.output_format_combo.currentText()
        self.settings.audio_quality = self.audio_quality_combo.currentText()
        self.settings.max_concurrent_conversions = self.max_concurrent_spin.value()
        self.settings.chunk_size_mb = self.chunk_size_spin.value()
        
        # 界面设置
        self.settings.theme = self.theme_combo.currentText()
        self.settings.language = self.language_combo.currentText()
        self.settings.window_width = self.window_width_spin.value()
        self.settings.window_height = self.window_height_spin.value()
        
        # 高级设置
        self.settings.log_level = self.log_level_combo.currentText()
        self.settings.enable_file_logging = self.enable_file_logging_cb.isChecked()
        self.settings.max_log_files = self.max_log_files_spin.value()
        self.settings.max_log_size_mb = self.max_log_size_spin.value()
        self.settings.enable_debug_mode = self.enable_debug_cb.isChecked()
        self.settings.send_usage_statistics = self.send_statistics_cb.isChecked()
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        current_dir = self.default_output_edit.text()
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择默认输出目录",
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            self.default_output_edit.setText(dir_path)
    
    def _reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self,
            "重置设置",
            "确定要重置所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from config.settings import get_default_settings
            self.settings = get_default_settings()
            self._load_current_settings()
            QMessageBox.information(self, "提示", "设置已重置为默认值")
    
    def _save_and_accept(self):
        """保存设置并接受"""
        try:
            self._save_current_settings()
            
            # 验证设置
            from ..config.settings import validate_settings
            errors = validate_settings(self.settings)
            if errors:
                error_msg = "设置验证失败：\n" + "\n".join(errors)
                QMessageBox.warning(self, "设置错误", error_msg)
                return
            
            # 保存设置
            if save_settings(self.settings):
                QMessageBox.information(self, "提示", "设置已保存")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时出错：{str(e)}")
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #e1e1e1;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin: 10px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background: white;
            }
            QCheckBox {
                spacing: 5px;
            }
        """)
