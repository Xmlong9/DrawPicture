#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform
import numpy as np
import math

class Shape:
    """基础图形类"""
    def __init__(self, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        # 图形属性
        self.color = color or QColor(0, 0, 0)
        self.fill_color = fill_color
        self.line_width = line_width
        self.line_style = line_style
        self.layer = layer  # 图层名称
        
        # 选择状态
        self.selected = False
        
        # 标记是否为橡皮擦
        self.is_eraser = False
        
        self.pen = QPen(self.color, self.line_width, self.line_style)
        self.brush = QBrush(Qt.transparent)  # 默认透明填充
        if self.fill_color is not None:
            self.brush = QBrush(self.fill_color)
            
        self.position = QPointF(0, 0)
        self.rotation = 0  # 旋转角度
        self.scale_x = 1.0  # X方向缩放因子
        self.scale_y = 1.0  # Y方向缩放因子
        self.z_value = 0  # z顺序，用于图层排序
        
    def __getstate__(self):
        """序列化时调用"""
        state = self.__dict__.copy()
        # 保存QPen的属性
        state['pen_color'] = self.pen.color().rgba()
        state['pen_width'] = self.pen.width()
        state['pen_style'] = int(self.pen.style())
        # 保存QBrush的属性
        state['brush_color'] = self.brush.color().rgba()
        state['brush_style'] = int(self.brush.style())
        # 保存QPointF的属性
        state['position_x'] = self.position.x()
        state['position_y'] = self.position.y()
        # 删除无法序列化的对象
        del state['pen']
        del state['brush']
        del state['position']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPen
        pen_color = QColor()
        pen_color.setRgba(state.pop('pen_color'))
        pen_width = state.pop('pen_width')
        pen_style = Qt.PenStyle(state.pop('pen_style'))
        self.pen = QPen(pen_color, pen_width, pen_style)
        
        # 恢复QBrush
        brush_color = QColor()
        brush_color.setRgba(state.pop('brush_color'))
        brush_style = Qt.BrushStyle(state.pop('brush_style'))
        self.brush = QBrush(brush_color, brush_style)
        
        # 恢复QPointF
        x = state.pop('position_x')
        y = state.pop('position_y')
        self.position = QPointF(x, y)
        
        # 恢复其他属性
        self.__dict__.update(state)
        
    def set_pen(self, pen):
        self.pen = pen
        
    def set_brush(self, brush):
        self.brush = brush
    
    def set_position(self, pos):
        self.position = pos
    
    def rotate(self, angle):
        """旋转图形"""
        self.rotation += angle
        
    def scale(self, factor):
        """缩放图形"""
        self.scale_x *= factor
        self.scale_y *= factor
        
    def contains(self, point):
        """检查点是否在图形内，考虑变换"""
        # 如果点在图形的边界矩形之外，快速返回False
        # 先转换边界矩形到全局坐标
        global_bounds = self._get_global_bounds()
        
        # 快速边界检查 - 如果点不在全局边界内，直接返回False
        if not global_bounds.contains(point):
            return False
            
        # 将全局坐标点转换为图形的本地坐标
        local_point = self._transform_point_to_local(point)
        
        # 交给子类判断点是否在图形内
        return self._contains_local(local_point)
        
    def _transform_point_to_local(self, point):
        """将全局坐标点转换为图形的本地坐标系"""
        # 创建转换矩阵
        transform = QTransform()
        # 反向应用变换（位置、旋转、缩放）
        transform.translate(self.position.x(), self.position.y())
        transform.rotate(self.rotation)
        transform.scale(self.scale_x, self.scale_y)
        # 计算逆变换
        inverted, success = transform.inverted()
        if not success:
            return point
        # 应用逆变换
        return inverted.map(point)
        
    def _get_global_bounds(self):
        """获取图形在全局坐标系中的边界矩形"""
        # 获取本地边界矩形，添加额外的边距使选择更容易
        local_rect = self.bounding_rect()
        
        # 添加额外的边距，考虑笔宽
        margin = max(10, self.pen.width())
        local_rect = local_rect.adjusted(-margin, -margin, margin, margin)
        
        # 创建变换矩阵
        transform = QTransform()
        transform.translate(self.position.x(), self.position.y())
        transform.rotate(self.rotation)
        transform.scale(self.scale_x, self.scale_y)
        
        # 变换矩形的四个角点
        path = QPainterPath()
        path.addRect(local_rect)
        transformed_path = transform.map(path)
        
        # 返回变换后路径的边界矩形
        return transformed_path.boundingRect()
        
    def _contains_local(self, point):
        """检查本地坐标点是否在图形内，由子类实现"""
        return False
        
    def bounding_rect(self):
        """获取图形的边界矩形"""
        return QRectF()
        
    def paint(self, painter):
        """绘制图形"""
        painter.save()
        # 应用变换
        painter.translate(self.position)
        painter.rotate(self.rotation)
        painter.scale(self.scale_x, self.scale_y)
        
        # 设置画笔和画刷
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        
        # 如果被选中，绘制选择指示器
        if self.selected:
            select_pen = QPen(Qt.blue, 1, Qt.DashLine)
            painter.setPen(select_pen)
            painter.setBrush(Qt.transparent)
            rect = self.bounding_rect()
            painter.drawRect(rect.adjusted(-3, -3, 3, 3))
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
        
        # 子类实现具体绘制逻辑
        self._draw(painter)
        
        painter.restore()
        
    def _draw(self, painter):
        """具体的绘制实现，由子类覆盖"""
        pass
    
    def clone(self):
        """创建图形的副本"""
        return Shape(self.color, self.fill_color, self.line_width, self.line_style, self.layer)


class Line(Shape):
    """直线"""
    def __init__(self, start=QPointF(0, 0), end=QPointF(100, 100), color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.start_point = start
        self.end_point = end
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QPointF的属性
        state['start_x'] = self.start_point.x()
        state['start_y'] = self.start_point.y()
        state['end_x'] = self.end_point.x()
        state['end_y'] = self.end_point.y()
        # 删除无法序列化的对象
        del state['start_point']
        del state['end_point']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPointF
        start_x = state.pop('start_x')
        start_y = state.pop('start_y')
        end_x = state.pop('end_x')
        end_y = state.pop('end_y')
        self.start_point = QPointF(start_x, start_y)
        self.end_point = QPointF(end_x, end_y)
        # 恢复其他属性
        super().__setstate__(state)
        
    def _draw(self, painter):
        painter.drawLine(self.start_point, self.end_point)
        
    def _contains_local(self, point):
        """检查点是否在线段上或附近"""
        # 计算点到线段的距离
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        x0, y0 = point.x(), point.y()
        
        # 计算线段长度的平方
        line_length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        # 如果线段长度为0，则直接计算点到起点的距离
        if line_length_squared == 0:
            distance = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            return distance <= max(5, self.pen.width() / 2)
            
        # 计算投影比例 t
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_squared))
        
        # 计算投影点坐标
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # 计算点到投影点的距离
        distance = math.sqrt((x0 - proj_x) ** 2 + (y0 - proj_y) ** 2)
        
        # 判断距离是否在笔宽的一半以内
        click_tolerance = max(5, self.pen.width() / 2)
        return distance <= click_tolerance
        
    def bounding_rect(self):
        """获取直线的边界矩形"""
        return QRectF(
            min(self.start_point.x(), self.end_point.x()),
            min(self.start_point.y(), self.end_point.y()),
            abs(self.end_point.x() - self.start_point.x()),
            abs(self.end_point.y() - self.start_point.y())
        )
        
    def clone(self):
        """创建直线的副本"""
        line_copy = Line(QPointF(self.start_point), QPointF(self.end_point), self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        line_copy.selected = False
        return line_copy


class Rectangle(Shape):
    """矩形"""
    def __init__(self, rect=QRectF(0, 0, 100, 80), color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.rect = rect
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QRectF的属性
        state['rect_x'] = self.rect.x()
        state['rect_y'] = self.rect.y()
        state['rect_width'] = self.rect.width()
        state['rect_height'] = self.rect.height()
        # 删除无法序列化的对象
        del state['rect']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QRectF
        x = state.pop('rect_x')
        y = state.pop('rect_y')
        width = state.pop('rect_width')
        height = state.pop('rect_height')
        self.rect = QRectF(x, y, width, height)
        # 恢复其他属性
        super().__setstate__(state)
        
    def _draw(self, painter):
        painter.drawRect(self.rect)
        
    def _contains_local(self, point):
        """检查点是否在矩形内"""
        return self.rect.contains(point)
        
    def bounding_rect(self):
        """获取矩形的边界"""
        return self.rect
        
    def clone(self):
        """创建矩形的副本"""
        rect_copy = Rectangle(QRectF(self.rect), self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        rect_copy.position = QPointF(self.position)
        rect_copy.rotation = self.rotation
        rect_copy.scale_x = self.scale_x
        rect_copy.scale_y = self.scale_y
        rect_copy.z_value = self.z_value
        return rect_copy


class Circle(Shape):
    """圆形"""
    def __init__(self, center=QPointF(0, 0), radius=50, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center
        self.radius = radius
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QPointF的属性
        state['center_x'] = self.center.x()
        state['center_y'] = self.center.y()
        state['radius'] = self.radius
        # 删除无法序列化的对象
        del state['center']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPointF和半径
        center_x = state.pop('center_x')
        center_y = state.pop('center_y')
        self.center = QPointF(center_x, center_y)
        self.radius = state.pop('radius')
        # 恢复其他属性
        super().__setstate__(state)
        
    def _draw(self, painter):
        painter.drawEllipse(self.center, self.radius, self.radius)
        
    def _contains_local(self, point):
        """检查点是否在圆内"""
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        return (dx * dx + dy * dy) <= (self.radius * self.radius)
        
    def bounding_rect(self):
        """获取圆的边界矩形"""
        return QRectF(
            self.center.x() - self.radius,
            self.center.y() - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def clone(self):
        """创建圆形的副本"""
        circle_copy = Circle(QPointF(self.center), self.radius, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        circle_copy.position = QPointF(self.position)
        circle_copy.rotation = self.rotation
        circle_copy.scale_x = self.scale_x
        circle_copy.scale_y = self.scale_y
        circle_copy.z_value = self.z_value
        return circle_copy


class ArchimedeanSpiral(Shape):
    """阿基米德螺旋线"""
    def __init__(self, center=QPointF(0, 0), a=0.25, b=0.25, turns=3, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center
        self.a = a  # 螺旋线参数a
        self.b = b  # 螺旋线参数b
        self.turns = turns  # 螺旋线圈数
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QPointF的属性
        state['center_x'] = self.center.x()
        state['center_y'] = self.center.y()
        # 删除无法序列化的对象
        del state['center']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPointF
        center_x = state.pop('center_x')
        center_y = state.pop('center_y')
        self.center = QPointF(center_x, center_y)
        # 恢复其他属性
        super().__setstate__(state)
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 计算螺线点
        first_point = True
        for theta in np.linspace(0, 2 * math.pi * self.turns, 500):
            r = self.a + self.b * theta
            x = r * math.cos(theta) + self.center.x()
            y = r * math.sin(theta) + self.center.y()
            
            if first_point:
                path.moveTo(x, y)
                first_point = False
            else:
                path.lineTo(x, y)
        
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在螺线上或附近"""
        # 获取点到中心的距离
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 计算角度
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        
        # 计算该角度对应的螺线半径
        turns_at_angle = angle / (2 * math.pi)
        max_turns = min(self.turns, turns_at_angle + self.turns)
        
        # 检查点是否在螺线的一定范围内
        tolerance = 5.0  # 点击容差，可以调整
        
        # 检查点是否在螺线最大范围内
        max_radius = self.a + self.b * (2 * math.pi * max_turns)
        if distance > max_radius:
            return False
            
        # 找到最接近的螺线点
        min_distance = float('inf')
        for theta in np.linspace(0, 2 * math.pi * self.turns, 100):
            r = self.a + self.b * theta
            x = r * math.cos(theta) + self.center.x()
            y = r * math.sin(theta) + self.center.y()
            
            dx_spiral = x - point.x()
            dy_spiral = y - point.y()
            dist_to_spiral = math.sqrt(dx_spiral*dx_spiral + dy_spiral*dy_spiral)
            
            min_distance = min(min_distance, dist_to_spiral)
            
        return min_distance <= tolerance
        
    def bounding_rect(self):
        """获取螺线的边界矩形"""
        # 最大半径是在最大角度时
        max_r = self.a + self.b * (2 * math.pi * self.turns)
        return QRectF(
            self.center.x() - max_r,
            self.center.y() - max_r,
            2 * max_r,
            2 * max_r
        )
        
    def clone(self):
        """创建螺旋线的副本"""
        spiral_copy = ArchimedeanSpiral(QPointF(self.center), self.a, self.b, self.turns, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        spiral_copy.position = QPointF(self.position)
        spiral_copy.rotation = self.rotation
        spiral_copy.scale_x = self.scale_x
        spiral_copy.scale_y = self.scale_y
        spiral_copy.z_value = self.z_value
        return spiral_copy


class SineCurve(Shape):
    """正弦曲线"""
    def __init__(self, start=QPointF(0, 0), amplitude=50, frequency=0.05, length=400, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.start = start
        self.amplitude = amplitude
        self.frequency = frequency
        self.length = length
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QPointF的属性
        state['start_x'] = self.start.x()
        state['start_y'] = self.start.y()
        # 删除无法序列化的对象
        del state['start']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPointF
        start_x = state.pop('start_x')
        start_y = state.pop('start_y')
        self.start = QPointF(start_x, start_y)
        # 恢复其他属性
        super().__setstate__(state)
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 增加采样点数量，使曲线更平滑
        num_points = 500  # 增加点数
        
        # 计算正弦曲线点
        first_point = True
        for x in np.linspace(0, self.length, num_points):
            y = self.amplitude * math.sin(x * self.frequency)
            
            if first_point:
                path.moveTo(x + self.start.x(), y + self.start.y())
                first_point = False
            else:
                path.lineTo(x + self.start.x(), y + self.start.y())
        
        # 使用抗锯齿绘制
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在正弦曲线上或附近"""
        # 检查点是否在曲线的横向范围内
        if point.x() < self.start.x() or point.x() > self.start.x() + self.length:
            return False
            
        # 计算在x位置的正弦值
        x_local = point.x() - self.start.x()
        expected_y = self.amplitude * math.sin(x_local * self.frequency) + self.start.y()
        
        # 检查点是否在曲线附近
        tolerance = 5.0  # 点击容差
        return abs(point.y() - expected_y) <= tolerance
        
    def bounding_rect(self):
        """获取正弦曲线的边界矩形"""
        return QRectF(
            self.start.x(),
            self.start.y() - self.amplitude,
            self.length,
            2 * self.amplitude
        )
        
    def clone(self):
        """创建正弦曲线的副本"""
        sine_copy = SineCurve(QPointF(self.start), self.amplitude, self.frequency, self.length, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        sine_copy.position = QPointF(self.position)
        sine_copy.rotation = self.rotation
        sine_copy.scale_x = self.scale_x
        sine_copy.scale_y = self.scale_y
        sine_copy.z_value = self.z_value
        return sine_copy


class Freehand(Shape):
    """自由绘制"""
    def __init__(self, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.points = []
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # 保存QPointF列表的属性
        state['points_x'] = [p.x() for p in self.points]
        state['points_y'] = [p.y() for p in self.points]
        # 删除无法序列化的对象
        del state['points']
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        # 恢复QPointF列表
        points_x = state.pop('points_x')
        points_y = state.pop('points_y')
        self.points = [QPointF(x, y) for x, y in zip(points_x, points_y)]
        # 恢复其他属性
        super().__setstate__(state)
        
    def add_point(self, point):
        self.points.append(point)
        
    def _draw(self, painter):
        if len(self.points) < 2:
            return
            
        # 创建路径
        path = QPainterPath()
        path.moveTo(self.points[0])
        
        for i in range(1, len(self.points)):
            path.lineTo(self.points[i])
            
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在自由绘制线条上或附近"""
        if len(self.points) < 2:
            return False
            
        # 设置点击容差
        click_tolerance = max(5, self.pen.width() / 2)
        
        # 检查点是否在任何线段附近
        for i in range(1, len(self.points)):
            # 获取线段的起点和终点
            x1, y1 = self.points[i-1].x(), self.points[i-1].y()
            x2, y2 = self.points[i].x(), self.points[i].y()
            x0, y0 = point.x(), point.y()
            
            # 计算线段长度的平方
            line_length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
            
            # 如果线段长度为0，则直接计算点到起点的距离
            if line_length_squared == 0:
                distance = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
                if distance <= click_tolerance:
                    return True
                continue
                
            # 计算投影比例 t
            t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_squared))
            
            # 计算投影点坐标
            proj_x = x1 + t * (x2 - x1)
            proj_y = y1 + t * (y2 - y1)
            
            # 计算点到投影点的距离
            distance = math.sqrt((x0 - proj_x) ** 2 + (y0 - proj_y) ** 2)
            
            # 判断距离是否在容差范围内
            if distance <= click_tolerance:
                return True
                
        return False
        
    def bounding_rect(self):
        """获取自由绘制线条的边界矩形"""
        if not self.points:
            return QRectF()
            
        min_x = min(point.x() for point in self.points)
        min_y = min(point.y() for point in self.points)
        max_x = max(point.x() for point in self.points)
        max_y = max(point.y() for point in self.points)
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        
    def clone(self):
        """创建自由绘制的副本"""
        freehand_copy = Freehand(self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        freehand_copy.points = [QPointF(p) for p in self.points]
        freehand_copy.position = QPointF(self.position)
        freehand_copy.rotation = self.rotation
        freehand_copy.scale_x = self.scale_x
        freehand_copy.scale_y = self.scale_y
        freehand_copy.z_value = self.z_value
        return freehand_copy


class ShapeGroup(Shape):
    """图形组"""
    def __init__(self, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.shapes = []
        
    def __getstate__(self):
        """序列化时调用"""
        state = super().__getstate__()
        # shapes列表中的每个图形都会自动调用其__getstate__方法
        return state
        
    def __setstate__(self, state):
        """反序列化时调用"""
        super().__setstate__(state)
        # shapes列表中的每个图形都会自动调用其__setstate__方法
        
    def add(self, shape):
        self.shapes.append(shape)
        
    def remove(self, shape):
        if shape in self.shapes:
            self.shapes.remove(shape)
            
    def _draw(self, painter):
        for shape in self.shapes:
            shape.paint(painter)
            
    def _contains_local(self, point):
        """检查点是否在组内任何图形内"""
        for shape in self.shapes:
            # 将点从组的局部坐标系转换到子图形的局部坐标系
            shape_point = shape._transform_point_to_local(point)
            if shape._contains_local(shape_point):
                return True
        return False
        
    def bounding_rect(self):
        """获取组合图形的边界矩形"""
        if not self.shapes:
            return QRectF()
            
        rects = [shape.bounding_rect() for shape in self.shapes]
        min_x = min(rect.left() for rect in rects)
        min_y = min(rect.top() for rect in rects)
        max_x = max(rect.right() for rect in rects)
        max_y = max(rect.bottom() for rect in rects)
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        
    def clone(self):
        """创建图形组的副本"""
        group_copy = ShapeGroup(self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        for shape in self.shapes:
            group_copy.add(shape.clone())
        group_copy.selected = False
        return group_copy


class MandelbrotSet(Shape):
    """曼德勃罗集"""
    def __init__(self, rect=QRectF(-2, -1.5, 3, 3), max_iter=100, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.rect = rect  # 复平面上的显示区域
        self.max_iter = max_iter  # 最大迭代次数
        
    def _draw(self, painter):
        width = int(self.rect.width() * 100)  # 分辨率
        height = int(self.rect.height() * 100)
        
        # 创建图像
        for px in range(width):
            for py in range(height):
                # 将像素坐标映射到复平面
                x = self.rect.x() + px * self.rect.width() / width
                y = self.rect.y() + py * self.rect.height() / height
                c = complex(x, y)
                
                # 计算该点是否属于曼德勃罗集
                z = complex(0, 0)
                for i in range(self.max_iter):
                    z = z * z + c
                    if abs(z) > 2:
                        break
                
                # 根据迭代次数设置颜色
                if i == self.max_iter - 1:
                    color = self.color
                else:
                    # 创建渐变色
                    hue = (i % 360) / 360.0
                    color = QColor.fromHsvF(hue, 1.0, 1.0)
                
                painter.setPen(color)
                painter.drawPoint(px, py)
        
    def _contains_local(self, point):
        """检查点是否在分形图形显示区域内"""
        return self.rect.contains(point)
        
    def bounding_rect(self):
        """获取分形图形的边界矩形"""
        return self.rect
        
    def clone(self):
        """创建分形图形的副本"""
        fractal_copy = MandelbrotSet(QRectF(self.rect), self.max_iter, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        fractal_copy.selected = False
        return fractal_copy


class JuliaSet(Shape):
    """朱利亚集"""
    def __init__(self, rect=QRectF(-1.5, -1.5, 3, 3), c=complex(-0.4, 0.6), max_iter=100, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.rect = rect  # 复平面上的显示区域
        self.c = c  # Julia集的参数
        self.max_iter = max_iter  # 最大迭代次数
        
    def _draw(self, painter):
        width = int(self.rect.width() * 100)  # 分辨率
        height = int(self.rect.height() * 100)
        
        # 创建图像
        for px in range(width):
            for py in range(height):
                # 将像素坐标映射到复平面
                x = self.rect.x() + px * self.rect.width() / width
                y = self.rect.y() + py * self.rect.height() / height
                z = complex(x, y)
                
                # 计算该点是否属于朱利亚集
                for i in range(self.max_iter):
                    z = z * z + self.c
                    if abs(z) > 2:
                        break
                
                # 根据迭代次数设置颜色
                if i == self.max_iter - 1:
                    color = self.color
                else:
                    # 创建渐变色
                    hue = (i % 360) / 360.0
                    color = QColor.fromHsvF(hue, 1.0, 1.0)
                
                painter.setPen(color)
                painter.drawPoint(px, py)
        
    def _contains_local(self, point):
        """检查点是否在分形图形显示区域内"""
        return self.rect.contains(point)
        
    def bounding_rect(self):
        """获取分形图形的边界矩形"""
        return self.rect
        
    def clone(self):
        """创建分形图形的副本"""
        julia_copy = JuliaSet(QRectF(self.rect), self.c, self.max_iter, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        julia_copy.selected = False
        return julia_copy


class SuperEllipse(Shape):
    """超椭圆（拉梅曲线）"""
    def __init__(self, center=QPointF(0, 0), a=100, b=100, n=2.5, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center  # 中心点
        self.a = a  # x轴半径
        self.b = b  # y轴半径
        self.n = n  # 拉梅参数
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 生成超椭圆的点
        points = []
        steps = 200
        for i in range(steps + 1):
            t = 2 * math.pi * i / steps
            # 超椭圆参数方程
            cos_t = math.cos(t)
            sin_t = math.sin(t)
            x = self.a * math.copysign(abs(cos_t) ** (2/self.n), cos_t)
            y = self.b * math.copysign(abs(sin_t) ** (2/self.n), sin_t)
            points.append(QPointF(x + self.center.x(), y + self.center.y()))
        
        # 绘制路径
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            path.closeSubpath()
            
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在超椭圆内"""
        # 将点转换到以中心为原点的坐标系
        x = (point.x() - self.center.x()) / self.a
        y = (point.y() - self.center.y()) / self.b
        # 超椭圆方程
        return abs(x) ** self.n + abs(y) ** self.n <= 1
        
    def bounding_rect(self):
        """获取超椭圆的边界矩形"""
        return QRectF(
            self.center.x() - self.a,
            self.center.y() - self.b,
            2 * self.a,
            2 * self.b
        )
        
    def clone(self):
        """创建超椭圆的副本"""
        ellipse_copy = SuperEllipse(QPointF(self.center), self.a, self.b, self.n, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        ellipse_copy.selected = False
        return ellipse_copy


class ParametricCurve(Shape):
    """参数化曲线（玫瑰线、心形线等）"""
    def __init__(self, center=QPointF(0, 0), radius=100, curve_type="rose", n=2, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center  # 中心点
        self.radius = radius  # 基础半径
        self.curve_type = curve_type  # 曲线类型
        self.n = n  # 参数（玫瑰线的瓣数等）
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 生成参数曲线的点
        points = []
        steps = 500
        
        if self.curve_type == "rose":
            # 玫瑰线
            for i in range(steps + 1):
                t = 2 * math.pi * i / steps
                r = self.radius * math.cos(self.n * t)
                x = r * math.cos(t)
                y = r * math.sin(t)
                points.append(QPointF(x + self.center.x(), y + self.center.y()))
                
        elif self.curve_type == "heart":
            # 心形线
            for i in range(steps + 1):
                t = 2 * math.pi * i / steps
                x = self.radius * math.sin(t) ** 3
                y = self.radius * (1.3 * math.cos(t) - 0.5 * math.cos(2*t) - 0.2 * math.cos(3*t) - 0.1 * math.cos(4*t))
                points.append(QPointF(x + self.center.x(), -y + self.center.y()))
                
        elif self.curve_type == "butterfly":
            # 蝴蝶线
            for i in range(steps + 1):
                t = 2 * math.pi * i / steps
                r = math.exp(math.cos(t)) - 2 * math.cos(4*t) - math.sin(t/12) ** 5
                x = self.radius * math.sin(t) * r
                y = self.radius * math.cos(t) * r
                points.append(QPointF(x + self.center.x(), y + self.center.y()))
        
        # 绘制路径
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            if self.curve_type != "butterfly":  # 蝴蝶线不闭合
                path.closeSubpath()
            
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在曲线附近"""
        # 简化为检查点是否在外接圆内
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        return dx*dx + dy*dy <= self.radius*self.radius
        
    def bounding_rect(self):
        """获取曲线的边界矩形"""
        # 根据不同曲线类型返回不同的边界
        if self.curve_type == "heart":
            return QRectF(
                self.center.x() - self.radius,
                self.center.y() - self.radius,
                2 * self.radius,
                2 * self.radius
            )
        else:
            return QRectF(
                self.center.x() - self.radius,
                self.center.y() - self.radius,
                2 * self.radius,
                2 * self.radius
            )
        
    def clone(self):
        """创建参数曲线的副本"""
        curve_copy = ParametricCurve(QPointF(self.center), self.radius, self.curve_type, self.n, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        curve_copy.selected = False
        return curve_copy


class Gear(Shape):
    """齿轮"""
    def __init__(self, center=QPointF(0, 0), outer_radius=100, tooth_count=20, tooth_depth=10, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center
        self.outer_radius = outer_radius
        self.tooth_count = tooth_count
        self.tooth_depth = tooth_depth
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 绘制齿轮轮廓
        angle_step = 2 * math.pi / (self.tooth_count * 2)  # 每个齿的角步长
        inner_radius = self.outer_radius - self.tooth_depth
        
        # 生成齿轮的点
        first_point = True
        for i in range(self.tooth_count * 2):
            angle = i * angle_step
            # 交替使用外半径和内半径
            radius = self.outer_radius if i % 2 == 0 else inner_radius
            x = self.center.x() + radius * math.cos(angle)
            y = self.center.y() + radius * math.sin(angle)
            
            if first_point:
                path.moveTo(x, y)
                first_point = False
            else:
                path.lineTo(x, y)
        
        path.closeSubpath()
        
        # 绘制中心圆
        center_radius = self.outer_radius * 0.2
        path.addEllipse(self.center, center_radius, center_radius)
        
        painter.drawPath(path)
        
    def _contains_local(self, point):
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        return dx*dx + dy*dy <= self.outer_radius*self.outer_radius
        
    def bounding_rect(self):
        return QRectF(
            self.center.x() - self.outer_radius,
            self.center.y() - self.outer_radius,
            2 * self.outer_radius,
            2 * self.outer_radius
        )
        
    def clone(self):
        gear_copy = Gear(QPointF(self.center), self.outer_radius, self.tooth_count, self.tooth_depth, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        gear_copy.selected = False
        return gear_copy


class Leaf(Shape):
    """树叶"""
    def __init__(self, center=QPointF(0, 0), size=100, angle=0, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center
        self.size = size
        self.angle = angle  # 旋转角度
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 保存当前变换
        painter.save()
        
        # 移动到中心点并旋转
        painter.translate(self.center)
        painter.rotate(self.angle)
        
        # 绘制叶片主体
        path.moveTo(0, -self.size/2)
        path.cubicTo(
            self.size/3, -self.size/2,  # 控制点1
            self.size/2, -self.size/6,  # 控制点2
            0, self.size/2  # 终点
        )
        path.cubicTo(
            -self.size/2, -self.size/6,  # 控制点1
            -self.size/3, -self.size/2,  # 控制点2
            0, -self.size/2  # 终点
        )
        
        # 绘制叶脉
        main_vein = QPainterPath()
        main_vein.moveTo(0, -self.size/2)
        main_vein.lineTo(0, self.size/2)
        
        # 绘制侧脉
        side_veins = QPainterPath()
        for i in range(5):
            y = -self.size/3 + i * self.size/3
            side_veins.moveTo(0, y)
            side_veins.quadTo(self.size/4, y + self.size/10, self.size/3, y + self.size/8)
            side_veins.moveTo(0, y)
            side_veins.quadTo(-self.size/4, y + self.size/10, -self.size/3, y + self.size/8)
        
        # 填充叶片
        if self.fill_color:
            painter.fillPath(path, QBrush(self.fill_color))
        
        # 绘制轮廓和叶脉
        painter.drawPath(path)
        painter.drawPath(main_vein)
        painter.drawPath(side_veins)
        
        # 恢复变换
        painter.restore()
        
    def _contains_local(self, point):
        # 转换点到叶片坐标系
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        # 简化为椭圆检测
        return (dx*dx)/(self.size*self.size/4) + (dy*dy)/(self.size*self.size) <= 1
        
    def bounding_rect(self):
        return QRectF(
            self.center.x() - self.size/2,
            self.center.y() - self.size/2,
            self.size,
            self.size
        )
        
    def clone(self):
        leaf_copy = Leaf(QPointF(self.center), self.size, self.angle, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        leaf_copy.selected = False
        return leaf_copy


class Cloud(Shape):
    """云朵"""
    def __init__(self, center=QPointF(0, 0), width=200, height=100, color=None, fill_color=None, line_width=1, line_style=Qt.SolidLine, layer="默认图层"):
        super().__init__(color, fill_color, line_width, line_style, layer)
        self.center = center
        self.width = width
        self.height = height
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 定义云朵的圆形组件
        circles = [
            (0, 0, self.height * 0.8),  # 中心圆
            (-self.width * 0.3, 0, self.height * 0.7),  # 左圆
            (self.width * 0.3, 0, self.height * 0.7),  # 右圆
            (-self.width * 0.15, -self.height * 0.2, self.height * 0.6),  # 左上圆
            (self.width * 0.15, -self.height * 0.2, self.height * 0.6),  # 右上圆
        ]
        
        # 绘制每个圆形
        first = True
        for x, y, r in circles:
            center = QPointF(self.center.x() + x, self.center.y() + y)
            if first:
                path.addEllipse(center, r, r)
                first = False
            else:
                sub_path = QPainterPath()
                sub_path.addEllipse(center, r, r)
                path = path.united(sub_path)
        
        # 填充云朵
        if self.fill_color:
            painter.fillPath(path, QBrush(self.fill_color))
        
        # 绘制轮廓
        painter.drawPath(path)
        
    def _contains_local(self, point):
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        # 简化为椭圆检测
        return (dx*dx)/(self.width*self.width/4) + (dy*dy)/(self.height*self.height/4) <= 1
        
    def bounding_rect(self):
        return QRectF(
            self.center.x() - self.width/2,
            self.center.y() - self.height/2,
            self.width,
            self.height
        )
        
    def clone(self):
        cloud_copy = Cloud(QPointF(self.center), self.width, self.height, self.color, self.fill_color, self.line_width, self.line_style, self.layer)
        cloud_copy.selected = False
        return cloud_copy 
