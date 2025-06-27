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
    selection_changed = pyqtSignal()  # 选择变化
    
    def __init__(self):
        super().__init__()
        self.shapes = []  # 存储所有图形
        self.selected_shapes = []  # 存储选中的图形
        self.file_path = None  # 文档文件路径
        self.modified = False  # 文档是否被修改
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.current_layer = 0  # 当前图层
        self.layers = [{'name': '默认图层', 'visible': True}]  # 图层列表
        
    def add_shape(self, shape):
        """添加图形到文档"""
        # 设置图形的z值为当前图层
        shape.z_value = self.current_layer
        
        # 记录操作用于撤销
        self.record_state()
        
        # 添加图形
        self.shapes.append(shape)
        
        self.set_modified(True)
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
    
    def get_shape_at(self, pos):
        """获取指定位置的图形"""
        # 倒序搜索以优先找到上层图形
        for shape in reversed(self.shapes):
            # 跳过不可见图层的图形
            if not self.layers[shape.z_value]['visible']:
                continue
                
            if shape.contains(pos):
                return shape
        return None
    
    def move_selected_shapes(self, delta):
        """移动选中的图形"""
        if not self.selected_shapes:
            return
            
        self.record_state()
        
        for shape in self.selected_shapes:
            shape.set_position(QPointF(shape.position.x() + delta.x(),
                                     shape.position.y() + delta.y()))
                                     
        self.set_modified(True)
        self.document_changed.emit()
    
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
        
        shapes_to_remove = list(self.selected_shapes)
        for shape in shapes_to_remove:
            self.shapes.remove(shape)
        
        self.selected_shapes.clear()
        
        self.set_modified(True)
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
        self.layers.append({'name': name, 'visible': True})
        self.current_layer = len(self.layers) - 1
        return self.current_layer
        
    def remove_layer(self, layer_index):
        """删除图层"""
        if layer_index < len(self.layers) and layer_index > 0:  # 不删除默认图层
            # 删除此图层上的所有图形
            self.record_state()
            self.shapes = [s for s in self.shapes if s.z_value != layer_index]
            
            # 调整更高层图形的z值
            for shape in self.shapes:
                if shape.z_value > layer_index:
                    shape.z_value -= 1
            
            # 删除图层
            self.layers.pop(layer_index)
            
            # 更新当前图层
            if self.current_layer >= len(self.layers):
                self.current_layer = len(self.layers) - 1
            elif self.current_layer == layer_index:
                self.current_layer = 0
                
            self.set_modified(True)
            self.document_changed.emit()
    
    def set_layer_visibility(self, layer_index, visible):
        """设置图层可见性"""
        if 0 <= layer_index < len(self.layers):
            self.layers[layer_index]['visible'] = visible
            self.document_changed.emit()
    
    def rename_layer(self, layer_index, name):
        """重命名图层"""
        if 0 <= layer_index < len(self.layers):
            self.layers[layer_index]['name'] = name
    
    def select_layer(self, layer_index):
        """选择当前图层"""
        if 0 <= layer_index < len(self.layers):
            self.current_layer = layer_index
    
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