#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal, QPointF
from PyQt5.QtGui import QPen, QBrush

from models.tools import (SelectionTool, LineTool, RectangleTool, CircleTool,
                        FreehandTool, SpiralTool, SineCurveTool, ColorTool, EraserTool,
                        PenTool)

class ToolController(QObject):
    """工具控制器类，管理所有工具和工具相关的交互"""
    
    tool_changed = pyqtSignal(str)  # 工具变更信号
    
    def __init__(self, document):
        super().__init__()
        self.document = document
        self.color_tool = ColorTool()
        self.init_tools()
        
    def init_tools(self):
        """初始化所有工具"""
        self.tools = {
            "selection": SelectionTool(self.document),
            "line": LineTool(self.document),
            "rectangle": RectangleTool(self.document),
            "circle": CircleTool(self.document),
            "freehand": FreehandTool(self.document),
            "spiral": SpiralTool(self.document),
            "sine": SineCurveTool(self.document),
            "eraser": EraserTool(self.document),
            "pen": PenTool(self.document)
        }
        
        # 默认使用选择工具
        self.current_tool_name = "selection"
        self.current_tool = self.tools["selection"]
        
    def set_tool(self, tool_name):
        """设置当前工具"""
        if tool_name in self.tools:
            self.current_tool_name = tool_name
            self.current_tool = self.tools[tool_name]
            self.tool_changed.emit(tool_name)
            
    def get_current_tool(self):
        """获取当前工具"""
        return self.current_tool
        
    def get_current_tool_name(self):
        """获取当前工具名称"""
        return self.current_tool_name
    
    def set_pen_color(self, color):
        """设置线条颜色"""
        self.color_tool.set_line_color(color)
        self._apply_color_to_selected_shapes(False)
        
    def set_fill_color(self, color):
        """设置填充颜色"""
        self.color_tool.set_fill_color(color)
        self._apply_color_to_selected_shapes(True)
        
    def set_line_width(self, width):
        """设置线宽"""
        self.color_tool.set_line_width(width)
        self._apply_line_width_to_selected_shapes()
        
    def set_line_style(self, style):
        """设置线型"""
        self.color_tool.set_line_style(style)
        self._apply_line_style_to_selected_shapes()
        
    def get_pen(self):
        """获取当前画笔"""
        return self.color_tool.get_pen()
        
    def get_brush(self):
        """获取当前画刷"""
        return self.color_tool.get_brush()
        
    def _apply_color_to_selected_shapes(self, is_fill):
        """应用颜色到选中图形"""
        if not self.document.selected_shapes:
            return
            
        self.document.record_state()
        for shape in self.document.selected_shapes:
            if is_fill:
                shape.set_brush(self.color_tool.get_brush())
            else:
                shape.set_pen(self.color_tool.get_pen())
        self.document.document_changed.emit()
        
    def _apply_line_width_to_selected_shapes(self):
        """应用线宽到选中图形"""
        if not self.document.selected_shapes:
            return
            
        width = self.color_tool.line_width
        self.document.record_state()
        for shape in self.document.selected_shapes:
            pen = QPen(shape.pen)
            pen.setWidth(width)
            shape.set_pen(pen)
        self.document.document_changed.emit()
        
    def _apply_line_style_to_selected_shapes(self):
        """应用线型到选中图形"""
        if not self.document.selected_shapes:
            return
            
        style = self.color_tool.line_style
        self.document.record_state()
        for shape in self.document.selected_shapes:
            pen = QPen(shape.pen)
            pen.setStyle(style)
            shape.set_pen(pen)
        self.document.document_changed.emit() 