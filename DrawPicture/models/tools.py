#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QCursor, QPixmap, QPainterPath, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint
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
        self.moving = False  # 是否正在移动
        self.click_threshold = 3  # 点击判定阈值（像素）
        self.last_position = None  # 上一次位置，用于计算微小移动
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            point = event.pos()
            self.last_position = point
            self.moving = False

            # 获取点击位置的图形
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
            current_pos = event.pos()
            # 计算移动距离
            move_distance = ((current_pos.x() - self.last_position.x()) ** 2 + 
                           (current_pos.y() - self.last_position.y()) ** 2) ** 0.5
                           
            # 只有移动足够距离才判定为拖动
            if move_distance > self.click_threshold or self.moving:
                self.moving = True
                delta = QPointF(current_pos - self.drag_start)
                self.document.move_selected_shapes(delta)
                self.drag_start = current_pos
            
            self.last_position = current_pos
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            # 如果没有移动，视为单击
            if not self.moving and self.drag_shape:
                # 单击已选中的图形时不做任何操作
                pass
            
            # 重置状态
            self.drag_start = None
            self.drag_shape = None
            self.moving = False
            self.last_position = None


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


class EraserTool(DrawingTool):
    """橡皮擦工具"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "橡皮擦"
        self.current_shape = None
        self.last_pos = None
        self.eraser_width = 20  # 橡皮擦宽度
        
        # 创建橡皮擦光标
        cursor_size = 32
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.transparent)  # 设置透明背景
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制橡皮擦图标
        # 主体部分（灰色矩形）
        painter.setPen(QPen(Qt.gray, 1))
        painter.setBrush(QBrush(Qt.lightGray))
        painter.drawRect(8, 2, 20, 16)
        
        # 底部部分（深灰色）
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.setBrush(QBrush(Qt.darkGray))
        painter.drawRect(8, 18, 20, 4)
        
        # 高光效果
        painter.setPen(QPen(Qt.white, 1))
        painter.drawLine(9, 3, 27, 3)
        
        painter.end()
        
        # 设置光标热点为橡皮擦的左下角
        self.cursor = QCursor(pixmap, 8, 22)
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.last_pos = event.pos()
            self.current_shape = Freehand()
            self.current_shape.add_point(event.pos())
            # 设置白色画笔
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(self.eraser_width)  # 使用较粗的线宽
            pen.setCapStyle(Qt.RoundCap)  # 设置圆形笔帽，使擦除更平滑
            pen.setJoinStyle(Qt.RoundJoin)  # 设置圆形连接点
            self.current_shape.set_pen(pen)
            # 设置白色填充
            brush = QBrush(QColor(255, 255, 255))
            self.current_shape.set_brush(brush)
            # 将图形添加到最顶层
            max_z = max([shape.z_value for shape in self.document.shapes]) if self.document.shapes else 0
            self.current_shape.z_value = max_z + 1
            self.document.add_shape(self.current_shape)
        
    def mouse_move(self, event):
        if self.is_drawing and self.current_shape:
            # 添加新的点
            current_pos = event.pos()
            # 如果与上一个点距离太远，创建新的形状以避免锯齿
            if self.last_pos and (current_pos - self.last_pos).manhattanLength() > self.eraser_width * 2:
                # 结束当前形状
                self.current_shape = None
                # 创建新的形状
                self.current_shape = Freehand()
                self.current_shape.add_point(self.last_pos)
                self.current_shape.add_point(current_pos)
                # 设置白色画笔
                pen = QPen(QColor(255, 255, 255))
                pen.setWidth(self.eraser_width)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                self.current_shape.set_pen(pen)
                # 设置白色填充
                brush = QBrush(QColor(255, 255, 255))
                self.current_shape.set_brush(brush)
                # 将图形添加到最顶层
                max_z = max([shape.z_value for shape in self.document.shapes]) if self.document.shapes else 0
                self.current_shape.z_value = max_z + 1
                self.document.add_shape(self.current_shape)
            else:
                self.current_shape.add_point(current_pos)
            
            self.last_pos = current_pos
            self.document.document_changed.emit()
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.current_shape = None
            self.last_pos = None


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


class PanTool(DrawingTool):
    """画布平移工具，用于拖拽移动视图"""
    def __init__(self, document):
        super().__init__(document)
        self.name = "平移"
        self.cursor = QCursor(Qt.OpenHandCursor)
        self.drag_start = None
        self.canvas = None  # 需要后续设置
        self.last_pos = None  # 上一次鼠标位置
        self.prev_delta = QPointF(0, 0)  # 上一次的移动向量
        self.smoothing_factor = 0.7  # 平滑因子 (0-1)，值越低越平滑
        self.max_speed = 10  # 每次移动的最大像素数
        self.moving = False
        self.accumulated_motion = QPointF(0, 0)  # 累积的微小移动
        
    def set_canvas(self, canvas):
        """设置关联的画布"""
        self.canvas = canvas
        
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.pos()
            self.last_pos = event.pos()
            self.prev_delta = QPointF(0, 0)
            self.moving = False
            self.accumulated_motion = QPointF(0, 0)
            self.cursor = QCursor(Qt.ClosedHandCursor)  # 改变光标为抓取状态
            if self.canvas:
                self.canvas.setCursor(self.cursor)
            
    def mouse_move(self, event):
        if self.drag_start and event.buttons() & Qt.LeftButton and self.canvas:
            current_pos = event.pos()
            
            # 获取当前缩放因子，并调整移动灵敏度
            zoom_factor = self.canvas.zoom_factor
            sensitivity_factor = min(1.0, zoom_factor)  # 缩小时降低灵敏度
            
            # 计算原始偏移量
            raw_delta = QPointF(current_pos - self.last_pos)
            
            # 累积微小移动，避免缩放小时微动无效
            self.accumulated_motion += raw_delta
            
            # 如果累积移动很小，且不在移动中，则忽略
            if (abs(self.accumulated_motion.x()) < 2/sensitivity_factor and 
                abs(self.accumulated_motion.y()) < 2/sensitivity_factor and 
                not self.moving):
                return
            
            # 到这一步，视为开始移动
            self.moving = True
            
            # 应用缩放因子调整移动灵敏度
            adjusted_delta = QPointF(
                raw_delta.x() * sensitivity_factor,
                raw_delta.y() * sensitivity_factor
            )
            
            # 限制最大速度
            max_adjusted_speed = self.max_speed * sensitivity_factor
            if abs(adjusted_delta.x()) > max_adjusted_speed:
                adjusted_delta.setX(max_adjusted_speed if adjusted_delta.x() > 0 else -max_adjusted_speed)
            if abs(adjusted_delta.y()) > max_adjusted_speed:
                adjusted_delta.setY(max_adjusted_speed if adjusted_delta.y() > 0 else -max_adjusted_speed)
            
            # 应用平滑 - 将当前移动与前一次移动混合
            smoothed_delta = QPointF(
                adjusted_delta.x() * self.smoothing_factor + self.prev_delta.x() * (1 - self.smoothing_factor),
                adjusted_delta.y() * self.smoothing_factor + self.prev_delta.y() * (1 - self.smoothing_factor)
            )
            
            # 更新前一次移动向量
            self.prev_delta = smoothed_delta
            
            # 重设累积运动
            self.accumulated_motion = QPointF(0, 0)
            
            # 转换为整数坐标
            final_delta = QPoint(int(smoothed_delta.x()), int(smoothed_delta.y()))
            
            # 只有实际有移动时才更新画布
            if not final_delta.isNull():
                self.canvas.pan_offset += final_delta
                self.canvas.update()
            
            # 更新上一次位置
            self.last_pos = current_pos
    
    def mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = None
            self.last_pos = None
            self.prev_delta = QPointF(0, 0)
            self.moving = False
            self.accumulated_motion = QPointF(0, 0)
            self.cursor = QCursor(Qt.OpenHandCursor)  # 恢复光标为开放手形
            if self.canvas:
                self.canvas.setCursor(self.cursor) 
