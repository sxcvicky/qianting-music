from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QGroupBox, QLabel, QProgressBar, QMessageBox)
from PyQt6.QtCore import pyqtSlot, Qt
import os 
from loguru import logger

from core.factory import ConverterFactory
from gui.workers import BatchConversionWorker

class BatchConversionTab(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.current_worker = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 文件列表组
        files_group = QGroupBox("文件列表")
        files_layout = QVBoxLayout(files_group)

        # 添加文件和清空按钮
        list_control_layout = QHBoxLayout()
        add_files_btn = QPushButton("添加文件")
        add_files_btn.clicked.connect(self._add_batch_files)

        clear_files_btn = QPushButton("清空列表")
        clear_files_btn.clicked.connect(self._clear_batch_files)

        list_control_layout.addWidget(add_files_btn)
        list_control_layout.addWidget(clear_files_btn)
        list_control_layout.addStretch()

        files_layout.addLayout(list_control_layout)

        # 文件列表
        self.batch_file_list = QListWidget()
        self.batch_file_list.setMinimumHeight(200)
        files_layout.addWidget(self.batch_file_list)

        layout.addWidget(files_group)

        # 批量转换控制
        batch_control_group = QGroupBox("批量转换控制")
        batch_control_layout = QVBoxLayout(batch_control_group)

        # 输出目录选择
        batch_output_layout = QHBoxLayout()
        self.batch_output_label = QLabel(self.settings.default_output_dir)
        self.batch_output_label.setObjectName("file_path_label")

        batch_output_btn = QPushButton("选择目录")
        batch_output_btn.clicked.connect(self._select_batch_output_dir)

        batch_output_layout.addWidget(QLabel("输出目录:"))
        batch_output_layout.addWidget(self.batch_output_label, 1)
        batch_output_layout.addWidget(batch_output_btn)

        batch_control_layout.addLayout(batch_output_layout)

        # 批量转换按钮
        self.batch_convert_btn = QPushButton("开始批量转换")
        self.batch_convert_btn.setObjectName("primary_btn")
        self.batch_convert_btn.setMinimumHeight(45)
        self.batch_convert_btn.clicked.connect(self._start_batch_conversion)
        batch_control_layout.addWidget(self.batch_convert_btn)

        # 批量进度条
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setMinimumHeight(25)
        batch_control_layout.addWidget(self.batch_progress_bar)

        # 批量状态标签
        self.batch_status_label = QLabel("就绪")
        self.batch_status_label.setObjectName("status_label")
        batch_control_layout.addWidget(self.batch_status_label)

        layout.addWidget(batch_control_group)

    def _add_batch_files(self):
        """添加批量文件"""
        # 移除 .mflac 扩展名（MFLAC 支持已下线）
        file_filter = "音频文件 (*.kgm *.ncm *.ogg *.qmc *.qmc0 *.qmc3 *.qmcflac *.wav);;所有文件 (*.*)"
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音频文件",
            self.settings.last_input_dir,
            file_filter
        )

        for file_path in file_paths:
            # 检查是否已存在
            if file_path not in [self.batch_file_list.item(i).text() for i in range(self.batch_file_list.count())]:
                self.batch_file_list.addItem(file_path)

        self._update_batch_convert_ready()

    def _clear_batch_files(self):
        """清空批量文件列表"""
        self.batch_file_list.clear()
        self._update_batch_convert_ready()

    def _update_batch_convert_ready(self):
        """更新批量转换准备状态"""
        has_files = self.batch_file_list.count() > 0
        self.batch_convert_btn.setEnabled(has_files)

        if has_files:
            self.batch_status_label.setText(f"准备就绪 (共 {self.batch_file_list.count()} 个文件)")
        else:
            self.batch_status_label.setText("请添加要转换的文件")

    def _start_batch_conversion(self):
        """开始批量转换"""
        if self.batch_file_list.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加要转换的文件")
            return

        output_dir = self.batch_output_label.text()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请先选择输出目录")
            return

        # 获取文件列表
        file_list = []
        for i in range(self.batch_file_list.count()):
            file_list.append(self.batch_file_list.item(i).text())

        # 禁用按钮
        self.batch_convert_btn.setEnabled(False)
        self.batch_convert_btn.setText("批量转换中...")

        # 重置进度条
        self.batch_progress_bar.setValue(0)
        self.batch_progress_bar.setMaximum(100)

        # 创建批量转换工作线程
        self.current_worker = BatchConversionWorker(file_list, output_dir)
        self.current_worker.file_started.connect(self._on_batch_file_started)
        self.current_worker.file_finished.connect(self._on_batch_file_finished)
        self.current_worker.progress.connect(self._on_batch_progress)
        self.current_worker.all_finished.connect(self._on_batch_all_finished)
        self.current_worker.error.connect(self._on_batch_error)
        self.current_worker.status_changed.connect(self._on_batch_status_changed)

        # 开始批量转换
        self.current_worker.start()

        logger.info(f"开始批量转换: {len(file_list)} 个文件")

    @pyqtSlot(str)
    def _on_batch_file_started(self, file_path):
        """批量转换开始处理文件"""
        self.batch_status_label.setText(f"正在转换: {os.path.basename(file_path)}")

    @pyqtSlot(str, object)
    def _on_batch_file_finished(self, file_path, result):
        """批量转换文件完成"""
        if result.success:
            pass

    @pyqtSlot(int, int)
    def _on_batch_progress(self, file_progress, overall_progress):
        """批量转换进度更新"""
        self.batch_progress_bar.setValue(overall_progress)

    @pyqtSlot(list)
    def _on_batch_all_finished(self, results):
        """批量转换全部完成"""
        self.batch_convert_btn.setEnabled(True)
        self.batch_convert_btn.setText("开始批量转换")
        self.batch_progress_bar.setValue(100)

        # 统计结果
        success_count = sum(1 for _, result in results if result.success)
        total_count = len(results)

        self.batch_status_label.setText(f"批量转换完成: {success_count}/{total_count} 成功")

        # 显示结果
        if success_count == total_count:
            QMessageBox.information(self, "成功", f"批量转换全部成功！\n\n共转换 {total_count} 个文件")
        else:
            failed_files = [file_path for file_path, result in results if not result.success]
            error_msg = f"批量转换完成，但有 {total_count - success_count} 个文件失败：\n\n"
            error_msg += "\n".join(failed_files[:5])  # 只显示前5个
            if len(failed_files) > 5:
                error_msg += "\n...等"
            QMessageBox.warning(self, "部分失败", error_msg)

        self.current_worker = None

    @pyqtSlot(str)
    def _on_batch_error(self, error_msg):
        """批量转换错误处理"""
        self.batch_convert_btn.setEnabled(True)
        self.batch_convert_btn.setText("开始批量转换")
        self.batch_progress_bar.setValue(0)
        self.batch_status_label.setText("批量转换错误")

        QMessageBox.critical(self, "错误", f"批量转换过程出错：{error_msg}")

        self.current_worker = None

    @pyqtSlot(str)
    def _on_batch_status_changed(self, status):
        """批量转换状态变化处理"""
        self.batch_status_label.setText(status)

    def _select_batch_output_dir(self):
        """选择批量输出目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择批量输出目录",
            self.settings.default_output_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if dir_path:
            self.batch_output_label.setText(dir_path)

    def update_output_dir_label(self, dir_path):
        """更新输出目录标签"""
        self.batch_output_label.setText(dir_path)
