class Styles:
    @staticmethod
    def get_stylesheet():
        return """
            QWidget {
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                font-size: 14px;
            }
            
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QMenuBar {
                background-color: #e0e0e0;
                border-bottom: 1px solid #c0c0c0;
            }
            
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #c0c0c0;
            }
            
            QMenu {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
            }
            
            QMenu::item {
                padding: 5px 20px;
            }
            
            QMenu::item:selected {
                background-color: #c0c0c0;
            }
            
            QToolBar {
                background: #e0e0e0;
                border-bottom: 1px solid #c0c0c0;
                padding: 5px;
                spacing: 10px;
            }
            
            QToolButton {
                background: #d0d0d0;
                border: 1px solid #b0b0b0;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 60px;
            }
            
            QToolButton:hover {
                background: #c0c0c0;
            }
            
            QToolButton:pressed {
                background: #b0b0b0;
            }
            
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: #ffffff;
            }
            
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom-color: #e0e0e0; /* same as pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff; /* same as pane color */
            }
            
            QTabBar::tab:hover {
                background: #d0d0d0;
            }
            
            QGroupBox {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 1ex; /* leave space for title */
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left; /* position at the top left */
                padding: 0 3px;
                background-color: #e0e0e0;
                border-radius: 3px;
            }
            
            QLabel {
                color: #333333;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                text-align: center;
                background-color: #e0e0e0;
            }
            
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 5px;
            }
            
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #c0c0c0;
            }
            
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 5px;
            }
            
            QTableWidget {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #e0e0e0;
            }
            
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #c0c0c0;
                font-weight: bold;
            }
            
            QScrollBar:vertical {
                border: 1px solid #999999;
                background: #f0f0f0;
                width: 10px;
                margin: 21px 0 21px 0;
            }
            
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
            }
            
            QScrollBar::add-line:vertical {
                border: 1px solid #999999;
                background: #f0f0f0;
                height: 20px;
                subcontrol-origin: bottom;
                subcontrol-position: bottom;
            }
            
            QScrollBar::sub-line:vertical {
                border: 1px solid #999999;
                background: #f0f0f0;
                height: 20px;
                subcontrol-origin: top;
                subcontrol-position: top left;
            }
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: 1px solid #999999;
                width: 3px;
                height: 3px;
                background: white;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                border: 1px solid #999999;
                background: #f0f0f0;
                height: 10px;
                margin: 0px 21px 0 21px;
            }
            
            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 20px;
            }
            
            QScrollBar::add-line:horizontal {
                border: 1px solid #999999;
                background: #f0f0f0;
                width: 20px;
                subcontrol-origin: right;
                subcontrol-position: right;
            }
            
            QScrollBar::sub-line:horizontal {
                border: 1px solid #999999;
                background: #f0f0f0;
                width: 20px;
                subcontrol-origin: left;
                subcontrol-position: top left;
            }
            
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                border: 1px solid #999999;
                width: 3px;
                height: 3px;
                background: white;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """