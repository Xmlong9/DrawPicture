#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QTransform
import numpy as np
import math

class Shape:
    """基础图形类"""
    def __init__(self):
        self.pen = QPen(Qt.black, 2, Qt.SolidLine)
        self.brush = QBrush(Qt.transparent)
        self.position = QPointF(0, 0)
        self.rotation = 0  # 旋转角度
        self.scale_factor = 1.0  # 缩放因子
        self.is_selected = False
        self.z_value = 0  # z顺序，用于图层排序
        
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
        self.scale_factor *= factor
        
    def contains(self, point):
        """检查点是否在图形内，考虑变换"""
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
        transform.scale(self.scale_factor, self.scale_factor)
        # 计算逆变换
        inverted, success = transform.inverted()
        if not success:
            return point
        # 应用逆变换
        return inverted.map(point)
        
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
        painter.scale(self.scale_factor, self.scale_factor)
        
        # 设置画笔和画刷
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        
        # 如果被选中，绘制选择指示器
        if self.is_selected:
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
        return Shape()


class Line(Shape):
    """直线"""
    def __init__(self, start=QPointF(0, 0), end=QPointF(100, 100)):
        super().__init__()
        self.start_point = start
        self.end_point = end
        
    def _draw(self, painter):
        painter.drawLine(self.start_point, self.end_point)
        
    def _contains_local(self, point):
        """检查点是否在线段上或附近"""
        line_path = QPainterPath()
        line_path.moveTo(self.start_point)
        line_path.lineTo(self.end_point)
        
        # 创建一个宽度为pen宽度的stroke path
        stroke_path = QPainterPath()
        stroke_pen = QPen(self.pen)
        stroke_pen.setWidth(max(5, self.pen.width()))
        stroke_path.addPath(line_path)
        
        return stroke_path.contains(point)
        
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
        line_copy = Line(QPointF(self.start_point), QPointF(self.end_point))
        line_copy.pen = QPen(self.pen)
        line_copy.brush = QBrush(self.brush)
        line_copy.position = QPointF(self.position)
        line_copy.rotation = self.rotation
        line_copy.scale_factor = self.scale_factor
        line_copy.is_selected = False
        return line_copy


class Rectangle(Shape):
    """矩形"""
    def __init__(self, rect=QRectF(0, 0, 100, 80)):
        super().__init__()
        self.rect = rect
        
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
        rect_copy = Rectangle(QRectF(self.rect))
        rect_copy.pen = QPen(self.pen)
        rect_copy.brush = QBrush(self.brush)
        rect_copy.position = QPointF(self.position)
        rect_copy.rotation = self.rotation
        rect_copy.scale_factor = self.scale_factor
        rect_copy.is_selected = False
        return rect_copy


class Circle(Shape):
    """圆形"""
    def __init__(self, center=QPointF(0, 0), radius=50):
        super().__init__()
        self.center = center
        self.radius = radius
        
    def _draw(self, painter):
        painter.drawEllipse(self.center, self.radius, self.radius)
        
    def _contains_local(self, point):
        """检查点是否在圆内"""
        dx = point.x() - self.center.x()
        dy = point.y() - self.center.y()
        return dx*dx + dy*dy <= self.radius*self.radius
        
    def bounding_rect(self):
        """获取圆的边界矩形"""
        return QRectF(
            self.center.x() - self.radius,
            self.center.y() - self.radius,
            2 * self.radius,
            2 * self.radius
        )
        
    def clone(self):
        """创建圆的副本"""
        circle_copy = Circle(QPointF(self.center), self.radius)
        circle_copy.pen = QPen(self.pen)
        circle_copy.brush = QBrush(self.brush)
        circle_copy.position = QPointF(self.position)
        circle_copy.rotation = self.rotation
        circle_copy.scale_factor = self.scale_factor
        circle_copy.is_selected = False
        return circle_copy


class ArchimedeanSpiral(Shape):
    """阿基米德螺线"""
    def __init__(self, center=QPointF(0, 0), a=0.25, b=0.25, turns=3):
        super().__init__()
        self.center = center
        self.a = a  # 螺线参数
        self.b = b  # 螺线参数
        self.turns = turns  # 螺线的圈数
        
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
        """创建螺线的副本"""
        spiral_copy = ArchimedeanSpiral(QPointF(self.center), self.a, self.b, self.turns)
        spiral_copy.pen = QPen(self.pen)
        spiral_copy.brush = QBrush(self.brush)
        spiral_copy.position = QPointF(self.position)
        spiral_copy.rotation = self.rotation
        spiral_copy.scale_factor = self.scale_factor
        spiral_copy.is_selected = False
        return spiral_copy


class SineCurve(Shape):
    """正弦曲线"""
    def __init__(self, start=QPointF(0, 0), amplitude=50, frequency=0.05, length=400):
        super().__init__()
        self.start_point = start
        self.amplitude = amplitude
        self.frequency = frequency
        self.length = length
        
    def _draw(self, painter):
        path = QPainterPath()
        
        # 计算正弦曲线点
        first_point = True
        for x in np.linspace(0, self.length, 200):
            y = self.amplitude * math.sin(x * self.frequency)
            
            if first_point:
                path.moveTo(x + self.start_point.x(), y + self.start_point.y())
                first_point = False
            else:
                path.lineTo(x + self.start_point.x(), y + self.start_point.y())
        
        painter.drawPath(path)
        
    def _contains_local(self, point):
        """检查点是否在正弦曲线上或附近"""
        # 检查点是否在曲线的横向范围内
        if point.x() < self.start_point.x() or point.x() > self.start_point.x() + self.length:
            return False
            
        # 计算在x位置的正弦值
        x_local = point.x() - self.start_point.x()
        expected_y = self.amplitude * math.sin(x_local * self.frequency) + self.start_point.y()
        
        # 检查点是否在曲线附近
        tolerance = 5.0  # 点击容差
        return abs(point.y() - expected_y) <= tolerance
        
    def bounding_rect(self):
        """获取正弦曲线的边界矩形"""
        return QRectF(
            self.start_point.x(),
            self.start_point.y() - self.amplitude,
            self.length,
            2 * self.amplitude
        )
        
    def clone(self):
        """创建正弦曲线的副本"""
        curve_copy = SineCurve(QPointF(self.start_point), self.amplitude, self.frequency, self.length)
        curve_copy.pen = QPen(self.pen)
        curve_copy.brush = QBrush(self.brush)
        curve_copy.position = QPointF(self.position)
        curve_copy.rotation = self.rotation
        curve_copy.scale_factor = self.scale_factor
        curve_copy.is_selected = False
        return curve_copy


class Freehand(Shape):
    """自由绘制"""
    def __init__(self):
        super().__init__()
        self.points = []  # 点列表
        
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
            
        # 创建路径
        path = QPainterPath()
        path.moveTo(self.points[0])
        
        for i in range(1, len(self.points)):
            path.lineTo(self.points[i])
            
        # 创建一个宽度为pen宽度的stroke path
        stroke_path = QPainterPath()
        stroke_pen = QPen(self.pen)
        stroke_pen.setWidth(max(5, self.pen.width()))
        stroke_path.addPath(path)
        
        return stroke_path.contains(point)
        
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
        """创建自由绘制线条的副本"""
        freehand_copy = Freehand()
        for point in self.points:
            freehand_copy.add_point(QPointF(point))
        freehand_copy.pen = QPen(self.pen)
        freehand_copy.brush = QBrush(self.brush)
        freehand_copy.position = QPointF(self.position)
        freehand_copy.rotation = self.rotation
        freehand_copy.scale_factor = self.scale_factor
        freehand_copy.is_selected = False
        return freehand_copy


class ShapeGroup(Shape):
    """图形组合"""
    def __init__(self):
        super().__init__()
        self.shapes = []  # 子图形列表
        
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
        """创建组合图形的副本"""
        group_copy = ShapeGroup()
        for shape in self.shapes:
            group_copy.add(shape.clone())
        group_copy.pen = QPen(self.pen)
        group_copy.brush = QBrush(self.brush)
        group_copy.position = QPointF(self.position)
        group_copy.rotation = self.rotation
        group_copy.scale_factor = self.scale_factor
        group_copy.is_selected = False
        return group_copy 