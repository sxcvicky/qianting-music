"""
重构版主程序入口
采用模块化架构的音频格式转换器
"""
import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.utils import setup_logging
from config import load_settings
from gui import MainWindow


def setup_application():
    """设置应用程序"""
    app = QApplication(sys.argv)
    app.setApplicationName("浅听音乐格式转换器")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("浅听音乐开发团队")
    app.setOrganizationDomain("qianting.music")
    
    # 设置应用图标
    icon_path = PROJECT_ROOT / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 设置高DPI支持
    # 注意：在较新版本的PyQt6中，这些属性可能已被弃用
    try:
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # 在较新版本的PyQt6中，高DPI支持是默认启用的
        pass
    
    return app


def setup_directories():
    """设置必要的目录"""
    directories = ['logs', 'output', 'assets']
    
    for dir_name in directories:
        dir_path = PROJECT_ROOT / dir_name
        dir_path.mkdir(exist_ok=True)


def setup_exception_handling():
    """设置全局异常处理"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = logging.getLogger(__name__)
        logger.critical("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
        
        error_msg = f"程序发生未预期的错误：\n\n{exc_type.__name__}: {exc_value}\n\n请查看日志文件获取详细信息。"
        
        # 创建一个临时应用来显示错误对话框
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        QMessageBox.critical(None, "程序错误", error_msg)
    
    sys.excepthook = handle_exception


def main():
    """主函数"""
    try:
        # 确保必要目录存在
        setup_directories()
        
        # 加载设置
        settings = load_settings()
        
        # 设置日志
        log_file = PROJECT_ROOT / "logs" / "converter.log" if settings.enable_file_logging else None
        log_level = getattr(logging, settings.log_level, logging.INFO)
        setup_logging(log_level, log_file)
        
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("浅听音乐格式转换器 v3.0.0 启动")
        logger.info("=" * 60)
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")
        logger.info(f"程序路径: {PROJECT_ROOT}")
        logger.info(f"调试模式: {settings.enable_debug_mode}")
        
        # 设置全局异常处理
        setup_exception_handling()
        
        # 创建Qt应用
        app = setup_application()
        
        # 创建主窗口
        try:
            window = MainWindow()
            window.show()
            
            logger.info("主窗口创建成功，程序准备就绪")
            
            # 运行应用
            exit_code = app.exec()
            
            logger.info(f"程序正常退出，退出码: {exit_code}")
            return exit_code
            
        except ImportError as e:
            error_msg = f"模块导入失败：{str(e)}\n\n请检查是否安装了所有必需的依赖包。"
            logger.error(error_msg)
            QMessageBox.critical(None, "导入错误", error_msg)
            return 1
            
        except Exception as e:
            error_msg = f"初始化失败：{str(e)}\n\n请查看日志文件获取详细信息。"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(None, "初始化错误", error_msg)
            return 1
    
    except Exception as e:
        # 最后的异常处理
        print(f"程序启动失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())