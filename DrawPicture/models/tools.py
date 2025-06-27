#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QCursor, QPixmap
import math

from models.shapes import Line, Rectangle, Circle, ArchimedeanSpiral, SineCurve, Freehand

class DrawingTool:
    """绘图工具基类"""
    def __init__(self, document):
        self.document = document
        self.is_drawing = False
        self.current_shape = None
        self.start_point = None
        self.cursor = QCursor(Qt.ArrowCursor)
        self.name = "工具"
        self.color_tool = None  # 添加颜色工具引用
        
    def set_color_tool(self, color_tool):
        """设置颜色工具"""
        self.color_tool = color_tool
        
    def mouse_press(self, event):
        """鼠标按下事件处理"""
        pass
        
    def mouse_move(self, event):
        """鼠标移动事件处理"""
        pass
        
    def mouse_release(self, event):
        """鼠标释放事件处理"""
        pass
        
    def get_cursor(self):
        """获取工具的光标"""
        return self.cursor
        
    def apply_current_style(self, shape):
        """应用当前样式到图形"""
        if self.color_tool:
            # 应用画笔
            shape.set_pen(self.color_tool.get_pen())
            # 应用画刷（填充）
            brush = self.color_tool.get_brush()
            shape.set_brush(brush)


class SelectionTool(DrawingTool):
    """选择工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "选择"
        self.drag_start = None
        self.drag_shape = None
        self.cursor = QCursor(Qt.ArrowCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            point = event.pos()
            shape = self.document.get_shape_at(point)
            
            # 检查是否点击了已选择的图形
            if shape and shape in self.document.selected_shapes:
                self.drag_start = point
                self.drag_shape = shape
            else:
                # 否则，选择新图形（如果有）
                multi_select = event.modifiers() & Qt.ShiftModifier
                if shape:
                    self.document.select_shape(shape, multi_select)
                else:
                    self.document.deselect_all()
                
                self.drag_start = point
                self.drag_shape = shape
        
    def mouse_move(self, event):
        if self.drag_start and (event.buttons() & Qt.LeftButton):
            delta = QPointF(event.pos() - self.drag_start)
            self.document.move_selected_shapes(delta)
            self.drag_start = event.pos()
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = None
            self.drag_shape = None


class LineTool(DrawingTool):
    """直线工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "直线"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.current_shape = Line(self.start_point, self.start_point)
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            # 更新线条终点
            self.current_shape.end_point = event.pos()
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 确保直线有一定长度
            dx = self.current_shape.end_point.x() - self.current_shape.start_point.x()
            dy = self.current_shape.end_point.y() - self.current_shape.start_point.y()
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 5:  # 最小长度阈值
                self.document.add_shape(self.current_shape)
            self.current_shape = None


class RectangleTool(DrawingTool):
    """矩形工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "矩形"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.current_shape = Rectangle(QRectF(self.start_point.x(), self.start_point.y(), 0, 0))
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            # 计算矩形区域
            pos = event.pos()
            rect = QRectF(
                min(self.start_point.x(), pos.x()),
                min(self.start_point.y(), pos.y()),
                abs(pos.x() - self.start_point.x()),
                abs(pos.y() - self.start_point.y())
            )
            self.current_shape.rect = rect
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 确保矩形有一定面积
            if self.current_shape.rect.width() > 5 and self.current_shape.rect.height() > 5:
                self.document.add_shape(self.current_shape)
            self.current_shape = None


class CircleTool(DrawingTool):
    """圆形工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "圆形"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.current_shape = Circle(self.start_point, 0)
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            # 计算半径
            dx = event.pos().x() - self.start_point.x()
            dy = event.pos().y() - self.start_point.y()
            radius = math.sqrt(dx*dx + dy*dy)
            self.current_shape.radius = radius
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 确保圆有一定半径
            if self.current_shape.radius > 5:
                self.document.add_shape(self.current_shape)
            self.current_shape = None


class FreehandTool(DrawingTool):
    """自由绘制工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "自由绘制"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.current_shape = Freehand()
            self.current_shape.add_point(event.pos())
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            self.current_shape.add_point(event.pos())
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 确保有足够多的点
            if len(self.current_shape.points) > 2:
                self.document.add_shape(self.current_shape)
            self.current_shape = None


class SpiralTool(DrawingTool):
    """阿基米德螺线工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "螺线"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            center = event.pos()
            self.start_point = center
            # 默认创建3圈螺线，a和b参数决定螺旋的松紧
            self.current_shape = ArchimedeanSpiral(center, 0.25, 0.25, 3)
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            # 根据鼠标位置调整螺线参数
            dx = event.pos().x() - self.start_point.x()
            dy = event.pos().y() - self.start_point.y()
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 调整螺线参数使其更美观
            if distance > 5:
                self.current_shape.b = max(0.1, min(1.0, distance / 100))
                self.current_shape.turns = max(1, min(10, int(distance / 20)))
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.document.add_shape(self.current_shape)
            self.current_shape = None


class SineCurveTool(DrawingTool):
    """正弦曲线工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "正弦曲线"
        self.cursor = QCursor(Qt.CrossCursor)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            # 默认参数
            self.current_shape = SineCurve(self.start_point, 50, 0.05, 400)
            if self.color_tool:
                self.apply_current_style(self.current_shape)
            self.is_drawing = True
        
    def mouse_move(self, event):
        if self.is_drawing:
            # 根据鼠标位置调整正弦曲线参数
            dx = event.pos().x() - self.start_point.x()
            dy = event.pos().y() - self.start_point.y()
            
            if abs(dx) > 5:
                # 调整长度和频率
                self.current_shape.length = max(100, abs(dx))
                self.current_shape.frequency = 0.01 + (abs(dx) % 5) * 0.01
                
            if abs(dy) > 5:
                # 调整振幅
                self.current_shape.amplitude = max(10, abs(dy))
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.document.add_shape(self.current_shape)
            self.current_shape = None


class ColorTool:
    """颜色工具类，用于管理线条颜色和填充颜色"""
    def __init__(self):
        # 预定义颜色
        self.predefined_colors = [
            QColor(0, 0, 0),       # 黑色
            QColor(255, 255, 255), # 白色
            QColor(255, 0, 0),     # 红色
            QColor(0, 255, 0),     # 绿色
            QColor(0, 0, 255),     # 蓝色
            QColor(255, 255, 0),   # 黄色
            QColor(0, 255, 255),   # 青色
            QColor(255, 0, 255),   # 洋红
            QColor(128, 128, 128), # 灰色
            QColor(165, 42, 42),   # 棕色
            QColor(255, 165, 0),   # 橙色
            QColor(128, 0, 128)    # 紫色
        ]
        
        self.line_color = QColor(0, 0, 0)  # 默认线条颜色为黑色
        
        # 创建透明填充颜色
        self.fill_color = QColor(255, 255, 255, 0)  # 完全透明的白色
        
        self.line_width = 2  # 默认线宽
        self.line_style = Qt.SolidLine  # 默认线型
        
    def get_pen(self):
        """获取当前画笔"""
        pen = QPen(self.line_color, self.line_width, self.line_style)
        return pen
        
    def get_brush(self):
        """获取当前画刷"""
        brush = QBrush(self.fill_color)
        return brush
        
    def set_line_color(self, color):
        """设置线条颜色"""
        self.line_color = color
        
    def set_fill_color(self, color):
        """设置填充颜色"""
        self.fill_color = color
        
    def set_line_width(self, width):
        """设置线宽"""
        self.line_width = width
        
    def set_line_style(self, style):
        """设置线型"""
        self.line_style = style 