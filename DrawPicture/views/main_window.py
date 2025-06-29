#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QAction, QFileDialog,
                         QMessageBox, QToolBar, QHBoxLayout, QWidget, QLabel)
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt

from models.document import DrawingDocument
from models.tools import (SelectionTool, LineTool, RectangleTool, CircleTool,
                         FreehandTool, SpiralTool, SineCurveTool, ColorTool, PanTool, EraserTool)
from views.canvas import Canvas
from views.panels import ToolPanel, ColorPanel, LayerPanel

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
        self.setWindowTitle("绘图与图形管理")
        self.resize(1200, 800)
        
    def init_tools(self):
        """初始化工具"""
        self.tools = {
            "selection": SelectionTool(self.document),
            "line": LineTool(self.document),
            "rectangle": RectangleTool(self.document),
            "circle": CircleTool(self.document),
            "freehand": FreehandTool(self.document),
            "spiral": SpiralTool(self.document),
            "sine": SineCurveTool(self.document)
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
        central_layout = QHBoxLayout(central_widget)
        
        # 创建画布
        self.canvas = Canvas(self.document)
        self.canvas.set_tool(self.current_tool)
        self.canvas.status_message.connect(self.set_status_message)
        central_layout.addWidget(self.canvas)
        
        # 为平移工具设置画布引用
        if "pan" in self.tools:
            self.tools["pan"].set_canvas(self.canvas)
        
        self.setCentralWidget(central_widget)
        
        # 创建工具面板
        self.tool_panel = ToolPanel()
        self.tool_panel.tool_selected.connect(self.on_tool_selected)
        self.create_dock_widget("工具", self.tool_panel, Qt.LeftDockWidgetArea)
        
        # 创建颜色面板
        self.color_panel = ColorPanel()
        self.color_panel.color_changed.connect(self.on_color_changed)
        self.color_panel.line_width_changed.connect(self.on_line_width_changed)
        self.color_panel.line_style_changed.connect(self.on_line_style_changed)
        self.create_dock_widget("颜色", self.color_panel, Qt.LeftDockWidgetArea)
        
        # 创建图层面板
        self.layer_panel = LayerPanel(self.document)
        self.create_dock_widget("图层", self.layer_panel, Qt.RightDockWidgetArea)
        
        # 创建菜单和工具栏
        self.create_menus()
        self.create_toolbars()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        self.status_label = QLabel("就绪")
        self.statusBar().addPermanentWidget(self.status_label)
        
    def create_dock_widget(self, title, widget, area):
        """创建停靠部件"""
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(area, dock)
        return dock
        
    def create_menus(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
    def create_toolbars(self):
        """创建工具栏"""
        # 创建一个简单的工具栏
        toolbar = QToolBar("主工具栏", self)
        self.addToolBar(toolbar)
        
        # 添加一些工具按钮
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.on_new)
        toolbar.addAction(new_action)
    
    def on_tool_selected(self, tool_name):
        """工具选择处理"""
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            self.canvas.set_tool(self.current_tool)
            self.set_status_message(f"当前工具: {self.current_tool.name}")
            
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
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "", "绘图文件 (*.draw);;所有文件 (*)"
            )
            if not file_path:
                return
            if not file_path.lower().endswith('.draw'):
                file_path += ".draw"
            self.document.save(file_path)
        else:
            self.document.save(self.document.file_path) 