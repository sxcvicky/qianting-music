"""
单文件转换标签页模块
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QProgressBar, QFileDialog
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QMessageBox
from core.factory import ConverterFactory


class SingleConversionTab(QWidget):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)

        # 输入文件
        input_layout = QHBoxLayout()
        self.input_file_label = QLabel("请选择要转换的文件")
        self.input_file_label.setObjectName("file_path_label")

        select_btn = QPushButton("选择文件")
        # select_btn.clicked.connect(self._select_input_file) # 连接将在MainWindow中处理

        input_layout.addWidget(QLabel("输入文件:"))
        input_layout.addWidget(self.input_file_label, 1)
        input_layout.addWidget(select_btn)

        file_layout.addLayout(input_layout)

        # 输出目录
        output_layout = QHBoxLayout()
        self.output_dir_label = QLabel(self.settings.default_output_dir if self.settings else "")
        self.output_dir_label.setObjectName("file_path_label")

        output_btn = QPushButton("选择目录")
        # output_btn.clicked.connect(self._select_output_dir) # 连接将在MainWindow中处理

        output_layout.addWidget(QLabel("输出目录:"))
        output_layout.addWidget(self.output_dir_label, 1)
        output_layout.addWidget(output_btn)

        file_layout.addLayout(output_layout)

        layout.addWidget(file_group)

        # 转换控制区域
        control_group = QGroupBox("转换控制")
        control_layout = QVBoxLayout(control_group)

        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setObjectName("primary_btn")
        self.convert_btn.setMinimumHeight(45)
        # self.convert_btn.clicked.connect(self._start_single_conversion) # 连接将在MainWindow中处理
        control_layout.addWidget(self.convert_btn)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        control_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("status_label")
        control_layout.addWidget(self.status_label)

        layout.addWidget(control_group)

        # 支持格式信息
        info_group = QGroupBox("支持格式")
        info_layout = QVBoxLayout(info_group)

        # format_info = self._get_format_info_text() # 此方法依赖于外部函数，将在MainWindow中传入
        self.format_label = QLabel("") # 初始为空，由外部设置
        self.format_label.setWordWrap(True)
        info_layout.addWidget(self.format_label)

        layout.addWidget(info_group)

        layout.addStretch()

        # 存储需要外部连接的控件
        self.select_file_btn = select_btn
        self.select_output_btn = output_btn

    def update_output_dir_label(self, path):
        self.output_dir_label.setText(path)

    def update_format_info(self, text):
        self.format_label.setText(text)

    def set_input_file_label(self, text):
        self.input_file_label.setText(text)

    def set_status_label(self, text):
        self.status_label.setText(text)

    def set_progress_bar_value(self, value):
        self.progress_bar.setValue(value)

    def enable_convert_button(self, enable):
        self.convert_btn.setEnabled(enable)

    def get_input_file_path(self):
        return self.input_file_label.text()

    def get_output_dir_path(self):
        return self.output_dir_label.text()

    def _select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.settings.default_output_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if dir_path:
            self.update_output_dir_label(dir_path)
            self.settings.last_output_dir = dir_path

    def _check_convert_ready(self):
        """检查是否准备好转换"""
        input_file = self.get_input_file_path()
        has_input = input_file and input_file != "请选择要转换的文件"
        
        # 检查是否支持该格式
        if has_input:
            is_supported = ConverterFactory.is_supported(input_file)
            if not is_supported:
                self.set_status_label("不支持的文件格式")
                self.enable_convert_button(False)
                return
        
        self.enable_convert_button(has_input)
        if has_input:
            self.set_status_label("准备就绪")
        else:
            self.set_status_label("请选择文件")

    @pyqtSlot(object)
    def _single_conversion_finished(self, result):
        """单文件转换完成"""
        success = result.success
        message = result.output_file if result.success else result.error_message
        
        self.enable_convert_button(True)
        self.set_progress_bar_value(100)
        
        if success:
            self.set_status_label("转换完成！")
            QMessageBox.information(self, "完成", f"转换成功！\n输出文件：{message}")
        else:
            self.set_status_label("转换失败")
            QMessageBox.critical(self, "错误", message)
    
    @pyqtSlot(int)
    def _on_conversion_progress(self, progress):
        """转换进度更新"""
        self.set_progress_bar_value(progress)
    
    @pyqtSlot(str)
    def _on_conversion_error(self, error_msg):
        """转换错误处理"""
        self.enable_convert_button(True)
        self.set_progress_bar_value(0)
        self.set_status_label("转换错误")

    @pyqtSlot(str)
    def _on_status_changed(self, status):
        """状态变化处理"""
        self.set_status_label(status)