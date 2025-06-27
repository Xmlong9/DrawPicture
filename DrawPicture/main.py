#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow

if __name__ == "__main__":
    # 确保当前目录是程序所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_()) 