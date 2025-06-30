#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QAction, QFileDialog,
                         QMessageBox, QToolBar, QHBoxLayout, QWidget, QLabel, QVBoxLayout)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QIcon, QBrush, QColor, QImage
from PyQt5.QtCore import Qt, QSize, QPoint, QRect

from DrawPicture.models.document import DrawingDocument
from DrawPicture.models.tools import (SelectionTool, LineTool, RectangleTool, CircleTool,
                         FreehandTool, SpiralTool, SineCurveTool, ColorTool, PanTool, EraserTool)
from DrawPicture.views.canvas import Canvas
from DrawPicture.views.panels import ToolPanel, ColorPanel, LayerPanel

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        
        # 创建文档
        self.document = DrawingDocument()
        
        # 创建颜色工具
        self.color_tool = ColorTool()
        
        # 初始化工具
        self.init_tools()
        
        # 初始化UI
        self.init_ui()
        
        # 设置窗口属性
        self.setWindowTitle("DrawPicture - 专业绘图工具")
        self.resize(1200, 800)
        
        # 创建应用程序图标
        self._create_app_icon()
        
        # 应用样式表
        self.apply_stylesheet()
        
        # 显示欢迎消息
        self.set_status_message("欢迎使用 DrawPicture 专业绘图工具")
        
        # 显示启动提示对话框
        self._show_welcome_dialog()
        
    def _create_app_icon(self):
        """创建应用程序图标"""
        icon_size = 64
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制彩色圆形
        colors = [
            QColor(255, 0, 0),    # 红
            QColor(0, 0, 255),    # 蓝
            QColor(0, 200, 0),    # 绿
            QColor(255, 200, 0),  # 黄
        ]
        
        # 绘制图标背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(240, 240, 240))
        painter.drawRoundedRect(0, 0, icon_size, icon_size, 10, 10)
        
        # 绘制彩色圆形
        radius = 12
        positions = [
            QPoint(20, 20),
            QPoint(44, 20),
            QPoint(20, 44),
            QPoint(44, 44)
        ]
        
        for i, (pos, color) in enumerate(zip(positions, colors)):
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(pos, radius, radius)
        
        # 绘制画笔图标
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(15, 15, 49, 49)
        painter.drawLine(15, 49, 49, 15)
        
        painter.end()
        
        # 设置应用程序图标
        self.setWindowIcon(QIcon(pixmap))
        
    def apply_stylesheet(self):
        """应用应用程序样式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QDockWidget {
                border: 1px solid #c0c0c0;
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }
            
            QDockWidget::title {
                background-color: #e0e0e0;
                padding: 6px;
                border-bottom: 1px solid #c0c0c0;
            }
            
            QGroupBox {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                background-color: #f8f8f8;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            
            QPushButton:checked {
                background-color: #c0c0c0;
                border: 2px solid #808080;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #c0c0c0;
                height: 8px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #5c9eff;
                border: 1px solid #5c9eff;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #3c7edd;
                border: 1px solid #3c7edd;
            }
            
            QComboBox {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-height: 24px;
            }
            
            QComboBox:editable {
                background: white;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #c0c0c0;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background-color: white;
            }
            
            QStatusBar {
                background-color: #e0e0e0;
                color: #333333;
            }
            
            QStatusBar QLabel {
                padding: 3px;
                border: none;
            }
            
            QToolBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
                spacing: 3px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
            }
            
            QToolBar QToolButton:pressed {
                background-color: #d0d0d0;
            }
            
            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
            }
            
            QMenuBar::item {
                spacing: 3px;
                padding: 3px 10px;
                background: transparent;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            
            QMenuBar::item:pressed {
                background-color: #d0d0d0;
            }
            
            QMenu {
                background-color: #f8f8f8;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
            }
            
            QMenu::item {
                padding: 5px 30px 5px 30px;
                border-radius: 3px;
            }
            
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
        """)
        
    def init_tools(self):
        """初始化工具"""
        self.tools = {
            "selection": SelectionTool(self.document),
            "pan": PanTool(self.document),  # 添加平移工具
            "line": LineTool(self.document),
            "rectangle": RectangleTool(self.document),
            "circle": CircleTool(self.document),
            "freehand": FreehandTool(self.document),
            "spiral": SpiralTool(self.document),
            "sine": SineCurveTool(self.document),
            "eraser": EraserTool(self.document)  # 添加橡皮擦工具
        }
        
        # 设置颜色工具
        for tool in self.tools.values():
            tool.set_color_tool(self.color_tool)
        
        # 为平移工具设置画布
        self.canvas = None  # 先声明一个占位符，稍后在init_ui中设置
        
        # 默认选择选择工具
        self.current_tool = self.tools["selection"]
        
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建画布
        self.canvas = Canvas(self.document)
        self.canvas.status_message.connect(self.set_status_message)
        self.canvas.zoom_changed.connect(self._update_zoom_indicator)
        central_layout.addWidget(self.canvas)
        
        # 为平移工具设置画布引用
        if "pan" in self.tools:
            self.tools["pan"].set_canvas(self.canvas)
        
        self.setCentralWidget(central_widget)
        
        # 创建工具面板
        self.tool_panel = ToolPanel()
        self.tool_panel.tool_selected.connect(self.on_tool_selected)
        self.create_dock_widget("工具箱", self.tool_panel, Qt.LeftDockWidgetArea)
        
        # 创建颜色面板
        self.color_panel = ColorPanel()
        self.color_panel.color_changed.connect(self.on_color_changed)
        self.color_panel.line_width_changed.connect(self.on_line_width_changed)
        self.color_panel.line_style_changed.connect(self.on_line_style_changed)
        self.color_panel.eraser_size_changed.connect(self.on_eraser_size_changed)
        self.color_panel.gradient_changed.connect(self.on_gradient_changed)
        self.color_panel.gradient_pen_changed.connect(self.on_gradient_pen_changed)
        self.create_dock_widget("颜色与样式", self.color_panel, Qt.LeftDockWidgetArea)
        
        # 创建图层面板
        self.layer_panel = LayerPanel(self.document)
        self.layer_panel.layer_changed.connect(self._update_layer_indicator)
        self.create_dock_widget("图层管理", self.layer_panel, Qt.RightDockWidgetArea)
        
        # 创建菜单和工具栏
        self.create_menus()
        self.create_toolbars()
        
        # 创建增强的状态栏
        self._setup_status_bar()
        
    def _setup_status_bar(self):
        """设置增强的状态栏"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #c0c0c0;
            }
            QStatusBar::item {
                border: none;
                padding: 3px;
            }
            QLabel {
                padding: 3px 10px;
            }
        """)
        
        # 状态消息
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_bar.addWidget(self.status_label)
        
        # 添加分隔符
        separator1 = QWidget()
        separator1.setFixedWidth(1)
        separator1.setFixedHeight(18)
        separator1.setStyleSheet("background-color: #c0c0c0;")
        status_bar.addPermanentWidget(separator1)
        
        # 添加当前工具指示器
        self.tool_indicator = QLabel("工具: 选择")
        status_bar.addPermanentWidget(self.tool_indicator)
        
        # 添加分隔符
        separator2 = QWidget()
        separator2.setFixedWidth(1)
        separator2.setFixedHeight(18)
        separator2.setStyleSheet("background-color: #c0c0c0;")
        status_bar.addPermanentWidget(separator2)
        
        # 添加当前图层指示器
        self.layer_indicator = QLabel("图层: 默认图层")
        status_bar.addPermanentWidget(self.layer_indicator)
        
        # 添加分隔符
        separator3 = QWidget()
        separator3.setFixedWidth(1)
        separator3.setFixedHeight(18)
        separator3.setStyleSheet("background-color: #c0c0c0;")
        status_bar.addPermanentWidget(separator3)
        
        # 添加缩放指示器
        self.zoom_indicator = QLabel("缩放: 100%")
        status_bar.addPermanentWidget(self.zoom_indicator)
        
    def create_dock_widget(self, title, widget, area):
        """创建停靠部件"""
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setMinimumWidth(150)  # 设置最小宽度
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # 设置标题样式
        dock.setStyleSheet("""
            QDockWidget::title {
                text-align: center;
                background-color: #e0e0e0;
                padding: 6px;
                font-weight: bold;
            }
        """)
        
        self.addDockWidget(area, dock)
        return dock
        
    def create_menus(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出图片(&E)...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.on_export_image)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&Q)", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.document.undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.document.redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        delete_action = QAction("删除选中图形(&D)", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(lambda: self.document.delete_selected_shapes())
        edit_menu.addAction(delete_action)
        
        # 视图菜单
        view_menu = self.menuBar().addMenu("视图(&V)")
        
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(lambda: self.canvas.zoom_in())
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(lambda: self.canvas.zoom_out())
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("重置缩放(&R)", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(lambda: self.canvas.zoom_reset())
        view_menu.addAction(zoom_reset_action)
        
        view_menu.addSeparator()
        
        # 添加网格显示/隐藏选项
        self.grid_action = QAction("显示网格(&G)", self)
        self.grid_action.setShortcut("Ctrl+G")
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(self.canvas.grid_visible)
        self.grid_action.triggered.connect(self.on_toggle_grid)
        view_menu.addAction(self.grid_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
        
    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于 DrawPicture",
                         "<h3>DrawPicture 1.0</h3>"
                         "<p>一个专业的绘图与图形管理工具</p>"
                         "<p>Copyright © 2025</p>")
    
    def on_tool_selected(self, tool_name):
        """工具选择处理"""
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            self.canvas.set_tool(self.current_tool)
            self.set_status_message(f"当前工具: {self.current_tool.name}")
            
            # 通知颜色面板当前工具已更改
            self.color_panel.set_current_tool(tool_name)
            
            # 更新状态栏工具指示器
            if hasattr(self, 'tool_indicator'):
                self.tool_indicator.setText(f"工具: {self.current_tool.name}")
            
    def on_color_changed(self, color, is_fill):
        """颜色变化处理"""
        if is_fill:
            self.color_tool.set_fill_color(color)
        else:
            self.color_tool.set_line_color(color)
            
        # 更新当前工具的颜色设置
        for tool in self.tools.values():
            if tool.current_shape:
                if is_fill:
                    tool.current_shape.set_brush(self.color_tool.get_brush())
                else:
                    tool.current_shape.set_pen(self.color_tool.get_pen())
        
        # 应用到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()  # 记录状态用于撤销
            for shape in self.document.selected_shapes:
                if is_fill:
                    shape.set_brush(self.color_tool.get_brush())
                else:
                    shape.set_pen(self.color_tool.get_pen())
            self.document.document_changed.emit()  # 更新显示
            
    def on_line_width_changed(self, width):
        """线宽变化处理"""
        self.color_tool.set_line_width(width)
        
        # 更新当前工具的线宽设置
        for tool in self.tools.values():
            if tool.current_shape:
                pen = QPen(tool.current_shape.pen)
                pen.setWidth(width)
                tool.current_shape.set_pen(pen)
        
        # 更新设置到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()
            for shape in self.document.selected_shapes:
                pen = QPen(shape.pen)
                pen.setWidth(width)
                shape.set_pen(pen)
            self.document.document_changed.emit()
            
    def on_line_style_changed(self, style):
        """线型变化处理"""
        self.color_tool.set_line_style(style)
        
        # 更新当前工具的线型设置
        for tool in self.tools.values():
            if tool.current_shape:
                pen = QPen(tool.current_shape.pen)
                pen.setStyle(style)
                tool.current_shape.set_pen(pen)
        
        # 更新设置到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()
            for shape in self.document.selected_shapes:
                pen = QPen(shape.pen)
                pen.setStyle(style)
                shape.set_pen(pen)
            self.document.document_changed.emit()
            
    def on_eraser_size_changed(self, size):
        """橡皮擦大小变化处理"""
        # 更新橡皮擦工具的大小设置
        if "eraser" in self.tools:
            self.tools["eraser"].set_eraser_size(size)
    
    def on_gradient_changed(self, start_color, end_color, gradient_type, direction):
        """渐变填充变化处理"""
        self.color_tool.set_gradient_fill(start_color, end_color, gradient_type, direction)
        
        # 应用到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()  # 记录状态用于撤销
            for shape in self.document.selected_shapes:
                shape.set_brush(self.color_tool.get_brush())
            self.document.document_changed.emit()  # 更新显示
            
    def on_gradient_pen_changed(self, start_color, end_color, gradient_type, direction):
        """渐变线条变化处理"""
        self.color_tool.set_gradient_pen(start_color, end_color, gradient_type, direction)
        
        # 应用到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()  # 记录状态用于撤销
            for shape in self.document.selected_shapes:
                shape.set_pen(self.color_tool.get_pen())
            self.document.document_changed.emit()  # 更新显示
    
    def set_status_message(self, message):
        """设置状态栏消息"""
        self.status_label.setText(message)
        
    def on_new(self):
        """新建文档"""
        self.document.new_document()
        
    def on_open(self):
        """打开文档"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "绘图文件 (*.draw);;所有文件 (*)"
        )
        if file_path:
            self.document.load(file_path)
            
    def on_save(self):
        """保存文档"""
        if not self.document.file_path:
            file_path, filter_type = QFileDialog.getSaveFileName(
                self, "保存文件", "", 
                "绘图文件 (*.draw);;PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg);;BMP图片 (*.bmp);;TIFF图片 (*.tiff);;WebP图片 (*.webp);;SVG图片 (*.svg);;所有文件 (*)"
            )
            if not file_path:
                return False
                
            # 根据选择的文件类型处理
            if "PNG" in filter_type:
                if not file_path.lower().endswith('.png'):
                    file_path += ".png"
                return self.on_export_image(file_path)
            elif "JPEG" in filter_type:
                if not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                return self.on_export_image(file_path)
            elif "BMP" in filter_type:
                if not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                return self.on_export_image(file_path)
            elif "TIFF" in filter_type:
                if not file_path.lower().endswith('.tiff'):
                    file_path += ".tiff"
                return self.on_export_image(file_path)
            elif "WebP" in filter_type:
                if not file_path.lower().endswith('.webp'):
                    file_path += ".webp"
                return self.on_export_image(file_path)
            elif "SVG" in filter_type:
                if not file_path.lower().endswith('.svg'):
                    file_path += ".svg"
                return self.on_export_image(file_path)
            else:
                if not file_path.lower().endswith('.draw'):
                    file_path += ".draw"
                self.document.file_path = file_path
            
        if self.document.save(self.document.file_path):
            self.set_status_message(f"文件已保存到: {self.document.file_path}")
            return True
        else:
            QMessageBox.warning(self, "保存失败", "无法保存文件。")
            return False

    def on_save_as(self):
        """另存为文档"""
        file_path, filter_type = QFileDialog.getSaveFileName(
            self, "另存为", "", 
            "绘图文件 (*.draw);;PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg);;BMP图片 (*.bmp);;TIFF图片 (*.tiff);;WebP图片 (*.webp);;SVG图片 (*.svg);;所有文件 (*)"
        )
        
        if file_path:
            # 根据选择的文件类型处理
            if "PNG" in filter_type:
                if not file_path.lower().endswith('.png'):
                    file_path += ".png"
                return self.on_export_image(file_path)
            elif "JPEG" in filter_type:
                if not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                return self.on_export_image(file_path)
            elif "BMP" in filter_type:
                if not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                return self.on_export_image(file_path)
            elif "TIFF" in filter_type:
                if not file_path.lower().endswith('.tiff'):
                    file_path += ".tiff"
                return self.on_export_image(file_path)
            elif "WebP" in filter_type:
                if not file_path.lower().endswith('.webp'):
                    file_path += ".webp"
                return self.on_export_image(file_path)
            elif "SVG" in filter_type:
                if not file_path.lower().endswith('.svg'):
                    file_path += ".svg"
                return self.on_export_image(file_path)
            else:
                if not file_path.lower().endswith('.draw'):
                    file_path += ".draw"
                    
                if self.document.save(file_path):
                    self.document.file_path = file_path
                    self.set_status_message(f"文件已保存到: {file_path}")
                    return True
                else:
                    QMessageBox.warning(self, "保存失败", "无法保存文件。")
        return False
        
    def on_export_image(self, file_path=None):
        """导出为图片"""
        if file_path is None:
            file_path, filter_type = QFileDialog.getSaveFileName(
                self, "导出图片", "", 
                "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg);;BMP图片 (*.bmp);;TIFF图片 (*.tiff);;WebP图片 (*.webp);;SVG图片 (*.svg);;ICO图标 (*.ico);;所有文件 (*)"
            )
            
            if file_path:
                # 设置默认扩展名
                if "PNG" in filter_type and not file_path.lower().endswith('.png'):
                    file_path += ".png"
                elif "JPEG" in filter_type and not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                elif "BMP" in filter_type and not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                elif "TIFF" in filter_type and not file_path.lower().endswith('.tiff'):
                    file_path += ".tiff"
                elif "WebP" in filter_type and not file_path.lower().endswith('.webp'):
                    file_path += ".webp"
                elif "SVG" in filter_type and not file_path.lower().endswith('.svg'):
                    file_path += ".svg"
                elif "ICO" in filter_type and not file_path.lower().endswith('.ico'):
                    file_path += ".ico"
        
        if file_path:
            try:
                # 创建高分辨率图像
                canvas_size = self.canvas.size()
                scale_factor = 2  # 使用整数倍数
                width = int(canvas_size.width() * scale_factor)
                height = int(canvas_size.height() * scale_factor)
                image = QImage(width, height, QImage.Format_ARGB32)
                image.fill(QColor(255, 255, 255))
                
                # 使用高质量渲染
                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.setRenderHint(QPainter.TextAntialiasing)
                
                # 应用缩放以提高分辨率
                painter.scale(scale_factor, scale_factor)
                self.canvas.render(painter)
                painter.end()
                
                # 根据文件类型设置保存选项
                save_options = {}
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    save_options['quality'] = 95  # JPEG质量设置（0-100）
                elif file_path.lower().endswith('.png'):
                    save_options['quality'] = 100  # PNG质量设置（0-100）
                    save_options['compression'] = 1  # PNG压缩级别（0-9）
                elif file_path.lower().endswith('.webp'):
                    save_options['quality'] = 95  # WebP质量设置（0-100）
                elif file_path.lower().endswith('.tiff'):
                    save_options['compression'] = 'lzw'  # TIFF压缩方式
                
                # 保存图片
                if image.save(file_path, quality=save_options.get('quality', -1)):
                    QMessageBox.information(self, "导出成功", 
                                         f"图片已导出到: {file_path}\n分辨率: {image.width()}x{image.height()}")
                    self.set_status_message(f"图片已导出到: {file_path}")
                    return True
                else:
                    QMessageBox.warning(self, "导出失败", "无法导出图片。")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", f"导出图片时发生错误：{str(e)}")
        return False

    def create_toolbars(self):
        """创建工具栏"""
        # 创建主工具栏
        toolbar = QToolBar("主工具栏", self)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # 文件操作
        new_action = self._create_action("新建", "document-new", "创建新文档", self.on_new)
        toolbar.addAction(new_action)
        
        open_action = self._create_action("打开", "document-open", "打开文档", self.on_open)
        toolbar.addAction(open_action)
        
        save_action = self._create_action("保存", "document-save", "保存文档", self.on_save)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 编辑操作
        undo_action = self._create_action("撤销", "edit-undo", "撤销上一步操作", lambda: self.document.undo())
        toolbar.addAction(undo_action)
        
        redo_action = self._create_action("重做", "edit-redo", "重做操作", lambda: self.document.redo())
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # 视图操作
        zoom_in_action = self._create_action("放大", "zoom-in", "放大视图", lambda: self.canvas.zoom_in())
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = self._create_action("缩小", "zoom-out", "缩小视图", lambda: self.canvas.zoom_out())
        toolbar.addAction(zoom_out_action)
        
        zoom_reset_action = self._create_action("重置缩放", "zoom-original", "重置缩放", lambda: self.canvas.zoom_reset())
        toolbar.addAction(zoom_reset_action)
        
        # 添加网格显示/隐藏按钮
        self.grid_toolbar_action = self._create_action("网格", "grid", "显示/隐藏网格", self.on_toggle_grid)
        self.grid_toolbar_action.setCheckable(True)
        self.grid_toolbar_action.setChecked(self.canvas.grid_visible)
        toolbar.addAction(self.grid_toolbar_action)
        
    def _create_action(self, text, icon_name, tooltip, slot):
        """创建一个工具栏动作"""
        action = QAction(text, self)
        
        # 创建图标
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据图标名称绘制不同的图标
        if icon_name == "document-new":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(QBrush(Qt.white))
            painter.drawRect(4, 4, 16, 16)
            painter.drawLine(8, 8, 8, 16)
            painter.drawLine(8, 8, 16, 8)
        elif icon_name == "document-open":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(QBrush(QColor(255, 240, 200)))
            painter.drawRect(4, 8, 16, 12)
            painter.drawLine(8, 8, 8, 4)
            painter.drawLine(8, 4, 16, 4)
            painter.drawLine(16, 4, 16, 8)
        elif icon_name == "document-save":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(QBrush(QColor(200, 220, 255)))
            painter.drawRect(4, 4, 16, 16)
            painter.drawRect(8, 10, 8, 6)
            painter.drawRect(7, 4, 10, 4)
        elif icon_name == "edit-undo":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawArc(4, 4, 16, 16, 90 * 16, 180 * 16)
            painter.drawLine(4, 12, 8, 8)
            painter.drawLine(4, 12, 8, 16)
        elif icon_name == "edit-redo":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawArc(4, 4, 16, 16, -90 * 16, 180 * 16)
            painter.drawLine(20, 12, 16, 8)
            painter.drawLine(20, 12, 16, 16)
        elif icon_name == "zoom-in":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(4, 4, 12, 12)
            painter.drawLine(14, 14, 20, 20)
            painter.drawLine(8, 10, 12, 10)
            painter.drawLine(10, 8, 10, 12)
        elif icon_name == "zoom-out":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(4, 4, 12, 12)
            painter.drawLine(14, 14, 20, 20)
            painter.drawLine(8, 10, 12, 10)
        elif icon_name == "zoom-original":
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(4, 4, 12, 12)
            painter.drawLine(14, 14, 20, 20)
            painter.drawText(QRect(6, 6, 8, 8), Qt.AlignCenter, "1")
        elif icon_name == "grid":
            # 绘制网格图标
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(4, 4, 16, 16)
            
            # 绘制网格线
            painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.DotLine))
            painter.drawLine(8, 4, 8, 20)
            painter.drawLine(12, 4, 12, 20)
            painter.drawLine(16, 4, 16, 20)
            painter.drawLine(4, 8, 20, 8)
            painter.drawLine(4, 12, 20, 12)
            painter.drawLine(4, 16, 20, 16)
        
        painter.end()
        
        action.setIcon(QIcon(pixmap))
        action.setToolTip(tooltip)
        action.triggered.connect(slot)
        
        return action
        
    def on_toggle_grid(self):
        """切换网格显示状态"""
        is_visible = self.canvas.toggle_grid()
        self.grid_action.setChecked(is_visible)
        self.grid_toolbar_action.setChecked(is_visible)
        if is_visible:
            self.grid_action.setText("隐藏网格(&G)")
            self.set_status_message("网格已显示")
        else:
            self.grid_action.setText("显示网格(&G)")
            self.set_status_message("网格已隐藏")

    def _update_zoom_indicator(self, zoom_factor):
        """更新缩放指示器"""
        if hasattr(self, 'zoom_indicator'):
            self.zoom_indicator.setText(f"缩放: {int(zoom_factor * 100)}%")
            
    def _update_layer_indicator(self, layer_name):
        """更新图层指示器"""
        if hasattr(self, 'layer_indicator'):
            self.layer_indicator.setText(f"图层: {layer_name}")
            
    def _show_welcome_dialog(self):
        """显示欢迎对话框"""
        msg = QMessageBox(self)
        msg.setWindowTitle("欢迎使用 DrawPicture")
        msg.setIconPixmap(self.windowIcon().pixmap(64, 64))
        msg.setText("<h3>欢迎使用 DrawPicture 专业绘图工具</h3>")
        msg.setInformativeText(
            "这是一个功能强大的绘图应用程序，提供了多种绘图工具和图层管理功能。\n\n"
            "<b>主要功能：</b>\n"
            "• 多种绘图工具（直线、矩形、圆形等）\n"
            "• 图层管理\n"
            "• 颜色和样式调整\n"
            "• 文件保存和加载\n\n"
            "开始使用左侧工具栏中的工具进行绘图吧！"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_() 