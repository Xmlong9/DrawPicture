#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QCursor
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal, QTime, QTimer

class Canvas(QWidget):
    """绘图画布"""
    
    # 自定义信号
    status_message = pyqtSignal(str)  # 状态消息信号
    zoom_changed = pyqtSignal(float)  # 添加缩放变化信号
    
    def __init__(self, document, parent=None):
        """初始化画布"""
        super().__init__(parent)
        
        # 存储文档引用
        self.document = document
        
        # 设置焦点策略，以便接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        
        # 设置画布属性
        self.current_tool = None  # 当前工具
        self.zoom_factor = 1.0  # 缩放因子
        self.pan_offset = QPoint(0, 0)  # 平移偏移量
        self.is_panning = False  # 是否正在平移
        self.last_pan_pos = None  # 上次平移位置
        
        # 网格设置
        self.grid_visible = False  # 默认不显示网格
        self.grid_size = 20  # 网格大小
        self.grid_color = QColor(220, 220, 220)  # 网格颜色
        
        # 设置画布背景色
        self.background_color = Qt.white
        p = self.palette()
        p.setColor(self.backgroundRole(), self.background_color)
        self.setPalette(p)
        
        # 缩放设置
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        
        # 绑定文档信号
        self.document.document_changed.connect(self.update)
        self.document.selection_changed.connect(self.update)
        
        # 设置画布属性
        self.setAttribute(Qt.WA_StaticContents)
        self.setMinimumSize(800, 600)
        
        # 设置背景色为白色
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        
        # 右键菜单相关
        self.context_menu = None
        self.last_context_pos = None
        
    def set_tool(self, tool):
        """设置当前工具"""
        self.current_tool = tool
        # 更新鼠标光标
        self.setCursor(tool.get_cursor())
        
    def create_context_menu(self, pos):
        """创建右键菜单"""
        self.last_context_pos = pos
        scene_pos = self.mapToScene(pos)
        
        # 检查是否点击了图形
        shape = self.document.get_shape_at(scene_pos)
        
        menu = QMenu(self)
        
        # 基本操作
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_selected_shapes)
        menu.addAction(copy_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_selected_shapes)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 图层操作
        layer_menu = QMenu("图层", self)
        
        # 获取所有图层
        layer_names = self.document.get_layer_names()
        for layer_name in layer_names:
            layer_action = QAction(layer_name, self)
            layer_action.setCheckable(True)
            layer_action.setChecked(layer_name == self.document.current_layer)
            layer_action.triggered.connect(lambda checked, name=layer_name: self.move_to_layer(name))
            layer_menu.addAction(layer_action)
        
        menu.addMenu(layer_menu)
        
        menu.addSeparator()
        
        # 选择操作
        select_all_action = QAction("全选", self)
        select_all_action.triggered.connect(self.select_all_shapes)
        menu.addAction(select_all_action)
        
        deselect_all_action = QAction("取消选择", self)
        deselect_all_action.triggered.connect(self.document.deselect_all)
        menu.addAction(deselect_all_action)
        
        # 根据是否有选中的图形启用/禁用菜单项
        has_selection = len(self.document.selected_shapes) > 0
        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)
        
        return menu
        
    def copy_selected_shapes(self):
        """复制选中的图形"""
        if self.document.selected_shapes:
            self.document.clone_selected_shapes()
            self.status_message.emit("已复制选中的图形")
            
    def delete_selected_shapes(self):
        """删除选中的图形"""
        if self.document.selected_shapes:
            self.document.delete_selected_shapes()
            self.status_message.emit("已删除选中的图形")
            
    def move_to_layer(self, layer_name):
        """将选中的图形移动到指定图层"""
        if not self.document.selected_shapes:
            return
            
        for shape in self.document.selected_shapes:
            shape.layer = layer_name
        self.document.document_changed.emit()
        self.status_message.emit(f"已移动到图层: {layer_name}")
        
    def select_all_shapes(self):
        """选择所有图形"""
        self.document.deselect_all()
        for shape in self.document.shapes:
            if self.document.is_layer_visible(shape.layer):
                self.document.select_shape(shape, True)
        self.status_message.emit("已选择所有图形")
        
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        menu = self.create_context_menu(event.pos())
        menu.exec_(event.globalPos())
        
    def paintEvent(self, event):
        """绘制事件处理"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置背景色
        painter.fillRect(self.rect(), self.background_color)
        
        # 先绘制网格（在坐标变换之前，确保网格覆盖整个可见区域）
        if self.grid_visible:
            self.draw_grid(painter)
        
        # 应用缩放和平移
        painter.translate(self.pan_offset)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # 绘制所有图形
        for shape in self.document.shapes:
            # 跳过不可见图层中的图形
            if self.document.is_layer_visible(shape.layer):
                # 保存画家状态
                painter.save()
                
                # 绘制图形
                shape.paint(painter)
                
                # 恢复画家状态
                painter.restore()
                
        # 绘制选择框
        for shape in self.document.selected_shapes:
            if self.document.is_layer_visible(shape.layer):
                painter.save()
                self.draw_selection_handles(painter, shape)
                painter.restore()
                
        # 绘制当前正在创建的图形
        if self.current_tool and self.current_tool.current_shape:
            self.current_tool.current_shape.paint(painter)
            
    def draw_grid(self, painter):
        """绘制网格 - 在视图坐标系中绘制，不受平移和缩放影响"""
        pen = QPen(self.grid_color)
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        
        # 计算可见区域
        width = self.width()
        height = self.height()
        
        # 计算网格线的间距（考虑缩放）
        grid_spacing = self.grid_size * self.zoom_factor
        
        # 计算起始位置（考虑偏移）
        offset_x = self.pan_offset.x()
        offset_y = self.pan_offset.y()
        
        # 计算第一条网格线的位置
        start_x = offset_x % grid_spacing
        if start_x < 0:
            start_x += grid_spacing
        
        start_y = offset_y % grid_spacing
        if start_y < 0:
            start_y += grid_spacing
        
        # 绘制垂直线
        x = start_x
        while x < width:
            x_int = int(x)
            painter.drawLine(QPoint(x_int, 0), QPoint(x_int, height))
            x += grid_spacing
            
        # 绘制水平线
        y = start_y
        while y < height:
            y_int = int(y)
            painter.drawLine(QPoint(0, y_int), QPoint(width, y_int))
            y += grid_spacing
        
    def draw_selection_handles(self, painter, shape):
        """绘制选择手柄"""
        rect = shape._get_global_bounds()
        
        # 设置手柄大小
        handle_size = 8
        half_handle = handle_size / 2
        
        # 绘制旋转手柄（顶部中心）
        rotation_handle_y = rect.top() - 20
        rotation_handle_x = rect.left() + rect.width() / 2
        
        # 绘制旋转图标
        painter.setPen(QPen(Qt.blue, 2))
        painter.setBrush(Qt.white)
        painter.drawEllipse(QPointF(rotation_handle_x, rotation_handle_y), handle_size, handle_size)
        
        # 绘制旋转箭头
        arrow_size = handle_size * 1.2
        painter.setPen(QPen(Qt.blue, 2))
        # 绘制圆弧箭头
        path = QPainterPath()
        path.moveTo(rotation_handle_x + arrow_size, rotation_handle_y)
        path.arcTo(rotation_handle_x - arrow_size, rotation_handle_y - arrow_size,
                  arrow_size * 2, arrow_size * 2, 0, 270)
        # 绘制箭头头部
        path.lineTo(rotation_handle_x + arrow_size/2, rotation_handle_y - arrow_size - arrow_size/4)
        path.lineTo(rotation_handle_x + arrow_size + arrow_size/4, rotation_handle_y - arrow_size)
        path.lineTo(rotation_handle_x + arrow_size, rotation_handle_y)
        painter.drawPath(path)
        
        # 绘制缩放手柄
        handles = [
            (rect.left(), rect.top()),  # 左上
            (rect.left() + rect.width()/2, rect.top()),  # 上中
            (rect.right(), rect.top()),  # 右上
            (rect.right(), rect.top() + rect.height()/2),  # 右中
            (rect.right(), rect.bottom()),  # 右下
            (rect.left() + rect.width()/2, rect.bottom()),  # 下中
            (rect.left(), rect.bottom()),  # 左下
            (rect.left(), rect.top() + rect.height()/2),  # 左中
        ]
        
        # 绘制白色方块手柄
        painter.setPen(QPen(Qt.blue, 1))
        painter.setBrush(Qt.white)
        for x, y in handles:
            painter.drawRect(QRectF(x - handle_size, y - handle_size,
                                  handle_size * 2, handle_size * 2))
                                  
        # 绘制选择框
        painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
            
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
            # 强制重绘画布，确保选择框随图形移动
            self.update()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.current_tool:
            scene_pos = self.mapToScene(event.pos())
            scene_event = type(event)(event.type(), scene_pos, event.button(),
                                   event.buttons(), event.modifiers())
            self.current_tool.mouse_release(scene_event)
            # 强制重绘画布，确保选择框位置更新
            self.update()
            
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 用于缩放"""
        if event.modifiers() & Qt.ControlModifier:
            # 放大或缩小
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # 默认滚动行为
            super().wheelEvent(event)
            
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
            
    def toggle_grid(self):
        """切换网格显示状态"""
        self.grid_visible = not self.grid_visible
        self.update()
        return self.grid_visible
        
    def set_grid_size(self, size):
        """设置网格大小"""
        self.grid_size = size
        if self.grid_visible:
            self.update()
            
    def zoom_in(self):
        """放大"""
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor = min(self.zoom_factor + self.zoom_step, self.max_zoom)
            self.zoom_changed.emit(self.zoom_factor)
        self.update()
        self.status_message.emit(f"缩放: {int(self.zoom_factor * 100)}%")
        
    def zoom_out(self):
        """缩小"""
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor = max(self.zoom_factor - self.zoom_step, self.min_zoom)
            self.zoom_changed.emit(self.zoom_factor)
        self.update()
        self.status_message.emit(f"缩放: {int(self.zoom_factor * 100)}%")
        
    def zoom_reset(self):
        """重置缩放"""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.zoom_changed.emit(self.zoom_factor)
        self.update()
        self.status_message.emit("缩放重置为 100%")
        
    def pan_canvas(self, dx, dy):
        """平移画布"""
        # 如果偏移量太小，忽略此次更新
        if abs(dx) < 1 and abs(dy) < 1:
            return
            
        # 检查是否需要限制更新频率
        current_time = QTime.currentTime()
        if self.last_pan_update is not None:
            elapsed = self.last_pan_update.msecsTo(current_time)
            if elapsed < self.min_update_interval:
                return  # 如果更新太频繁，则跳过
        
        # 更新平移偏移量
        self.pan_offset += QPoint(dx, dy)
        self.last_pan_update = current_time
        
        # 使用update()而不是repaint()，效率更高
        self.update() 
        
        # 更新状态栏坐标
        center = QPointF(self.width()/2, self.height()/2)
        scene_center = self.mapToScene(center.toPoint())
        self.status_message.emit(f"中心坐标: ({int(scene_center.x())}, {int(scene_center.y())})")
        
    def screen_to_world(self, screen_x, screen_y):
        """将屏幕坐标转换为世界坐标"""
        # 考虑平移和缩放
        world_x = (screen_x - self.pan_offset.x()) / self.zoom_factor
        world_y = (screen_y - self.pan_offset.y()) / self.zoom_factor
        return world_x, world_y
        
    def world_to_screen(self, world_x, world_y):
        """将世界坐标转换为屏幕坐标"""
        # 考虑平移和缩放
        screen_x = world_x * self.zoom_factor + self.pan_offset.x()
        screen_y = world_y * self.zoom_factor + self.pan_offset.y()
        return screen_x, screen_y 