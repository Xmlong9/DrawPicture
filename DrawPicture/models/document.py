#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal, QPointF, QFileInfo
from PyQt5.QtGui import QColor
import pickle
import os

class DrawingDocument(QObject):
    """图形文档类，管理所有图形对象"""
    
    # 定义信号
    document_changed = pyqtSignal()  # 文档内容发生变化
    document_saved = pyqtSignal(str)  # 文档保存信号，参数为保存路径
    selection_changed = pyqtSignal()  # 选择变化
    layers_changed = pyqtSignal()  # 图层变化
    
    def __init__(self):
        """初始化绘图文档"""
        super().__init__()
        
        # 图形列表
        self.shapes = []
        self.selected_shapes = []  # 存储选中的图形
        
        # 文件信息
        self.file_path = None  # 文档文件路径
        self.modified = False  # 文档是否被修改
        
        # 撤销/重做栈
        self.undo_stack = []
        self.redo_stack = []
        
        # 图层列表
        self.layers = []
        self.current_layer = "默认图层"  # 当前图层名称
        self.add_layer("默认图层")  # 添加默认图层
        
    def add_shape(self, shape):
        """添加图形"""
        self.record_state()
        self.shapes.append(shape)
        self.modified = True
        self.document_changed.emit()
        
    def remove_shape(self, shape):
        """从文档中删除图形"""
        if shape in self.shapes:
            # 记录操作用于撤销
            self.record_state()
            
            self.shapes.remove(shape)
            if shape in self.selected_shapes:
                self.selected_shapes.remove(shape)
                self.selection_changed.emit()
            
            self.set_modified(True)
            self.document_changed.emit()
            
    def clear(self):
        """清空文档"""
        if self.shapes:
            self.record_state()
            self.shapes.clear()
            self.selected_shapes.clear()
            self.set_modified(True)
            self.document_changed.emit()
            self.selection_changed.emit()
            
    def select_shape(self, shape, multi_select=False):
        """选择图形"""
        if not multi_select:
            # 如果不是多选，先取消所有选择
            if self.selected_shapes:
                old_selected = list(self.selected_shapes)
                self.selected_shapes.clear()
                for s in old_selected:
                    s.is_selected = False
        
        if shape in self.shapes and shape not in self.selected_shapes:
            self.selected_shapes.append(shape)
            shape.is_selected = True
            self.selection_changed.emit()
    
    def deselect_shape(self, shape):
        """取消选择图形"""
        if shape in self.selected_shapes:
            self.selected_shapes.remove(shape)
            shape.is_selected = False
            self.selection_changed.emit()
    
    def deselect_all(self):
        """取消所有选择"""
        if self.selected_shapes:
            for shape in self.selected_shapes:
                shape.is_selected = False
            self.selected_shapes.clear()
            self.selection_changed.emit()
    
    def get_shape_at(self, point, exclude_eraser=False):
        """获取指定点上的图形"""
        # 从后向前遍历（顶层优先）
        for shape in reversed(self.shapes):
            # 跳过不可见图层中的图形
            if not self.is_layer_visible(shape.layer):
                continue
                
            # 如果指定了排除橡皮擦，则跳过橡皮擦图形
            if exclude_eraser and shape.is_eraser:
                continue
                
            # 检查点是否在图形内
            if shape.contains(point):
                return shape
                
        return None
    
    def move_selected_shapes(self, delta):
        """移动选中的图形"""
        if not self.selected_shapes:
            return
        
        for shape in self.selected_shapes:
            if hasattr(shape, 'position'):
                # 更新图形位置
                shape.position = QPointF(shape.position.x() + delta.x(), 
                                      shape.position.y() + delta.y())
                
        # 发送文档变化信号，强制重绘画布
        self.document_changed.emit()
        # 发送选择变化信号，确保选择框也更新
        self.selection_changed.emit()
    
    def rotate_selected_shapes(self, angle):
        """旋转选中的图形"""
        if not self.selected_shapes:
            return
            
            self.record_state()
        
        for shape in self.selected_shapes:
            shape.rotate(angle)
            
        self.set_modified(True)
        self.document_changed.emit()
    
    def scale_selected_shapes(self, factor):
        """缩放选中的图形"""
        if not self.selected_shapes:
            return
            
            self.record_state()
        
        for shape in self.selected_shapes:
            shape.scale(factor)
            
        self.set_modified(True)
        self.document_changed.emit()
    
    def clone_selected_shapes(self):
        """复制选中的图形"""
        if not self.selected_shapes:
            return
            
            self.record_state()
        
        new_shapes = []
        for shape in self.selected_shapes:
            clone = shape.clone()
            # 稍微偏移一点位置
            clone.set_position(QPointF(clone.position.x() + 10, 
                                     clone.position.y() + 10))
            clone.z_value = self.current_layer
            self.shapes.append(clone)
            new_shapes.append(clone)
        
        # 选择新复制的图形
        self.deselect_all()
        for shape in new_shapes:
            self.select_shape(shape, True)
            
        self.set_modified(True)
        self.document_changed.emit()
    
    def delete_selected_shapes(self):
        """删除选中的图形"""
        if not self.selected_shapes:
            return
            
            self.record_state()
        for shape in self.selected_shapes:
            if shape in self.shapes:
                self.shapes.remove(shape)
        
        self.selected_shapes.clear()
        self.modified = True
        self.document_changed.emit()
        self.selection_changed.emit()
    
    def bring_to_front(self, shape=None):
        """将图形置于顶层"""
        if shape is None:
            if not self.selected_shapes:
                return
            shape = self.selected_shapes[0]
            
        self.record_state()
        
        self.shapes.remove(shape)
        self.shapes.append(shape)
        
        self.set_modified(True)
        self.document_changed.emit()
    
    def send_to_back(self, shape=None):
        """将图形置于底层"""
        if shape is None:
            if not self.selected_shapes:
                return
            shape = self.selected_shapes[0]
            
        self.record_state()
        
        self.shapes.remove(shape)
        self.shapes.insert(0, shape)
        
        self.set_modified(True)
        self.document_changed.emit()
    
    # 图层操作
    def add_layer(self, name="新图层"):
        """添加新图层"""
        if name not in [layer['name'] for layer in self.layers]:
            self.layers.append({
                'name': name,
                'visible': True,
                'locked': False,
                'opacity': 1.0
            })
            self.current_layer = name
            self._notify_layers_changed()
            return True
        return False
        
    def remove_layer(self, name):
        """删除图层"""
        # 不允许删除最后一个图层
        if len(self.layers) <= 1:
            return False
            
        # 记录状态用于撤销/重做
            self.record_state()
            
        # 查找图层索引
        layer_index = -1
        for i, layer in enumerate(self.layers):
            if layer['name'] == name:
                layer_index = i
                break
                
        if layer_index >= 0:
            # 删除该图层中的所有图形
            shapes_to_remove = [shape for shape in self.shapes if shape.layer == name]
            for shape in shapes_to_remove:
                if shape in self.shapes:
                    self.shapes.remove(shape)
                if shape in self.selected_shapes:
                    self.selected_shapes.remove(shape)
            
            # 删除图层
            del self.layers[layer_index]
            
            # 如果删除的是当前图层，则选择第一个图层
            if self.current_layer == name:
                self.current_layer = self.layers[0]['name']
                
            self.modified = True
            self._notify_layers_changed()
            self._notify_document_changed()
            self.selection_changed.emit()
            return True
        return False
    
    def rename_layer(self, old_name, new_name):
        """重命名图层"""
        # 检查新名称是否已存在
        if new_name in [layer['name'] for layer in self.layers]:
            return False
            
        # 查找图层
        for layer in self.layers:
            if layer['name'] == old_name:
                layer['name'] = new_name
                
                # 更新图形中的图层引用
                for shape in self.shapes:
                    if shape.layer == old_name:
                        shape.layer = new_name
                        
                # 更新当前图层引用
                if self.current_layer == old_name:
                    self.current_layer = new_name
                    
                self._notify_layers_changed()
                self._notify_document_changed()
                return True
        return False
    
    def move_layer_up(self, name):
        """上移图层"""
        # 查找图层索引
        layer_index = -1
        for i, layer in enumerate(self.layers):
            if layer['name'] == name:
                layer_index = i
                break
                
        if layer_index > 0:  # 不是第一个图层
            # 记录状态用于撤销/重做
            self.record_state()
            
            # 交换图层
            self.layers[layer_index], self.layers[layer_index - 1] = \
                self.layers[layer_index - 1], self.layers[layer_index]
                
            self.modified = True
            self._notify_layers_changed()
            return True
        return False
    
    def move_layer_down(self, name):
        """下移图层"""
        # 查找图层索引
        layer_index = -1
        for i, layer in enumerate(self.layers):
            if layer['name'] == name:
                layer_index = i
                break
                
        if layer_index >= 0 and layer_index < len(self.layers) - 1:  # 不是最后一个图层
            # 记录状态用于撤销/重做
            self.record_state()
            
            # 交换图层
            self.layers[layer_index], self.layers[layer_index + 1] = \
                self.layers[layer_index + 1], self.layers[layer_index]
                
            self.modified = True
            self._notify_layers_changed()
            return True
        return False
    
    def set_current_layer(self, name):
        """设置当前图层"""
        for layer in self.layers:
            if layer['name'] == name:
                self.current_layer = name
                self._notify_layers_changed()
                return True
        return False
    
    def is_layer_visible(self, name):
        """检查图层是否可见"""
        for layer in self.layers:
            if layer['name'] == name:
                return layer['visible']
        return False
    
    def set_layer_visibility(self, name, visible):
        """设置图层可见性"""
        for layer in self.layers:
            if layer['name'] == name:
                layer['visible'] = visible
                self._notify_layers_changed()
                self._notify_document_changed()
                return True
        return False
    
    def is_layer_locked(self, name):
        """检查图层是否锁定"""
        for layer in self.layers:
            if layer['name'] == name:
                return layer.get('locked', False)
        return False
    
    def set_layer_locked(self, name, locked):
        """设置图层锁定状态"""
        for layer in self.layers:
            if layer['name'] == name:
                layer['locked'] = locked
                self._notify_layers_changed()
                return True
        return False
    
    def get_layer_opacity(self, name):
        """获取图层透明度"""
        for layer in self.layers:
            if layer['name'] == name:
                return layer.get('opacity', 1.0)
        return 1.0
    
    def set_layer_opacity(self, name, opacity):
        """设置图层透明度"""
        for layer in self.layers:
            if layer['name'] == name:
                layer['opacity'] = max(0.0, min(1.0, opacity))  # 限制在0-1范围内
                self._notify_layers_changed()
                self._notify_document_changed()
                return True
        return False
    
    def get_layer_names(self):
        """获取所有图层名称"""
        return [layer['name'] for layer in self.layers]
    
    def _notify_layers_changed(self):
        """通知图层变化"""
        if self.layers_changed:
            self.layers_changed.emit()
            
    def _notify_document_changed(self):
        """通知文档变化"""
        if self.document_changed:
            self.document_changed.emit()
    
    # 文档操作
    def new_document(self):
        """新建文档"""
        self.clear()
        self.shapes.clear()
        self.selected_shapes.clear()
        self.file_path = None
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_layer = 0
        self.layers = [{'name': '默认图层', 'visible': True}]
        self.set_modified(False)
        self.document_changed.emit()
        self.selection_changed.emit()
    
    def save(self, filepath):
        """保存文档"""
        try:
            with open(filepath, 'wb') as f:
                data = {
                    'shapes': self.shapes,
                    'layers': self.layers,
                    'current_layer': self.current_layer
                }
                pickle.dump(data, f)
                
            self.file_path = filepath
            self.set_modified(False)
            self.document_saved.emit(filepath)
            return True
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    def load(self, filepath):
        """加载文档"""
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                
            self.shapes = data.get('shapes', [])
            self.layers = data.get('layers', [{'name': '默认图层', 'visible': True}])
            self.current_layer = data.get('current_layer', 0)
            self.selected_shapes.clear()
            self.file_path = filepath
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.set_modified(False)
            self.document_changed.emit()
            self.selection_changed.emit()
            
            return True
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            return False
    
    def get_file_name(self):
        """获取文档文件名"""
        if self.file_path:
            return QFileInfo(self.file_path).fileName()
        return "无标题"
    
    # 撤销重做相关
    def record_state(self):
        """记录当前状态用于撤销"""
        # 创建所有图形的副本
        state = []
        for shape in self.shapes:
            state.append(shape.clone())
            
        self.undo_stack.append({
            'shapes': state,
            'layers': self.layers.copy(),
            'current_layer': self.current_layer
        })
        
        # 清空重做栈
        self.redo_stack.clear()
        
        # 限制撤销栈大小
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)
    
    def undo(self):
        """撤销"""
        if not self.undo_stack:
            return False
            
        # 保存当前状态到重做栈
        current_state = []
        for shape in self.shapes:
            current_state.append(shape.clone())
            
        self.redo_stack.append({
            'shapes': current_state,
            'layers': self.layers.copy(),
            'current_layer': self.current_layer
        })
        
        # 恢复上一个状态
        state = self.undo_stack.pop()
        self.shapes = state['shapes']
        self.layers = state['layers']
        self.current_layer = state['current_layer']
        
        # 清空选择
        self.selected_shapes.clear()
        
        self.set_modified(True)
        self.document_changed.emit()
        self.selection_changed.emit()
        
        return True
    
    def redo(self):
        """重做"""
        if not self.redo_stack:
            return False
            
        # 保存当前状态到撤销栈
        current_state = []
        for shape in self.shapes:
            current_state.append(shape.clone())
            
        self.undo_stack.append({
            'shapes': current_state,
            'layers': self.layers.copy(),
            'current_layer': self.current_layer
        })
        
        # 恢复下一个状态
        state = self.redo_stack.pop()
        self.shapes = state['shapes']
        self.layers = state['layers']
        self.current_layer = state['current_layer']
        
        # 清空选择
        self.selected_shapes.clear()
        
        self.set_modified(True)
        self.document_changed.emit()
        self.selection_changed.emit()
        
        return True
    
    def can_undo(self):
        """是否可以撤销"""
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        """是否可以重做"""
        return len(self.redo_stack) > 0
    
    def set_modified(self, modified):
        """设置文档修改状态"""
        self.modified = modified 