#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal

class Canvas(QWidget):
    """绘图画布"""
    
    # 自定义信号
    status_message = pyqtSignal(str)  # 状态消息信号
    
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.current_tool = None
        self.grid_visible = False
        self.grid_size = 20
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        
        # 绑定文档信号
        self.document.document_changed.connect(self.update)
        self.document.selection_changed.connect(self.update)
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        
        # 设置焦点策略，允许接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 设置画布属性
        self.setAttribute(Qt.WA_StaticContents)
        self.setMinimumSize(800, 600)
        
        # 设置背景色为白色
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        
    def set_tool(self, tool):
        """设置当前工具"""
        self.current_tool = tool
        self.setCursor(tool.get_cursor())
        
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 应用缩放和平移
        painter.translate(self.pan_offset)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # 绘制网格
        if self.grid_visible:
            self._draw_grid(painter)
        
        # 绘制所有图形
        for shape in self.document.shapes:
            # 检查图层是否可见
            if shape.z_value < len(self.document.layers) and self.document.layers[shape.z_value]['visible']:
                shape.paint(painter)
                
        # 绘制当前正在创建的图形
        if self.current_tool and self.current_tool.current_shape:
            self.current_tool.current_shape.paint(painter)
            
    def _draw_grid(self, painter):
        """绘制网格"""
        pen = QPen(QColor(200, 200, 200))
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        
        # 计算当前可见区域
        rect = self.rect()
        top_left = self.mapToScene(rect.topLeft())
        bottom_right = self.mapToScene(rect.bottomRight())
        
        # 绘制垂直线
        x = int(top_left.x() / self.grid_size) * self.grid_size
        while x <= bottom_right.x():
            painter.drawLine(x, top_left.y(), x, bottom_right.y())
            x += self.grid_size
            
        # 绘制水平线
        y = int(top_left.y() / self.grid_size) * self.grid_size
        while y <= bottom_right.y():
            painter.drawLine(top_left.x(), y, bottom_right.x(), y)
            y += self.grid_size
            
    def mapToScene(self, point):
        """将窗口坐标映射到场景坐标"""
        return QPointF(
            (point.x() - self.pan_offset.x()) / self.zoom_factor,
            (point.y() - self.pan_offset.y()) / self.zoom_factor
        )
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.current_tool:
            # 将窗口坐标转换为场景坐标
            scene_pos = self.mapToScene(event.pos())
            # 创建具有场景坐标的新事件
            scene_event = type(event)(event.type(), scene_pos, event.button(),
                                   event.buttons(), event.modifiers())
            self.current_tool.mouse_press(scene_event)
            self.update()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        scene_pos = self.mapToScene(event.pos())
        
        # 发送状态栏消息
        self.status_message.emit(f"坐标: ({int(scene_pos.x())}, {int(scene_pos.y())})")
        
        if self.current_tool:
            # 创建具有场景坐标的新事件
            scene_event = type(event)(event.type(), scene_pos, event.button(),
                                   event.buttons(), event.modifiers())
            self.current_tool.mouse_move(scene_event)
            self.update()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.current_tool:
            scene_pos = self.mapToScene(event.pos())
            scene_event = type(event)(event.type(), scene_pos, event.button(),
                                   event.buttons(), event.modifiers())
            self.current_tool.mouse_release(scene_event)
            self.update()
            
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 用于缩放"""
        if event.modifiers() & Qt.ControlModifier:
            # 计算缩放因子
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
                
            # 应用缩放
            old_zoom = self.zoom_factor
            self.zoom_factor *= factor
            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))  # 限制缩放范围
            
            # 更新画布
            self.update()
            
    def keyPressEvent(self, event):
        """键盘事件处理"""
        # 删除选中图形
        if event.key() == Qt.Key_Delete:
            self.document.delete_selected_shapes()
            
        # 复制选中图形
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.document.clone_selected_shapes()
            
        # 撤销操作
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.document.undo()
            
        # 重做操作
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.document.redo()
            
    def toggle_grid(self, visible=None):
        """切换网格显示"""
        if visible is None:
            self.grid_visible = not self.grid_visible
        else:
            self.grid_visible = visible
        self.update()
        
    def set_grid_size(self, size):
        """设置网格大小"""
        self.grid_size = size
        if self.grid_visible:
            self.update()
            
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        self.zoom_factor = min(10.0, self.zoom_factor)  # 限制最大缩放
        self.update()
        
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        self.zoom_factor = max(0.1, self.zoom_factor)  # 限制最小缩放
        self.update()
        
    def zoom_reset(self):
        """重置缩放"""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update()
        
    def pan_canvas(self, dx, dy):
        """平移画布"""
        self.pan_offset += QPoint(dx, dy)
        self.update() 