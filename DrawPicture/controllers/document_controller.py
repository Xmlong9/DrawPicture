#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPainter, QColor

import os

class DocumentController(QObject):
    """文档控制器类，处理文档的操作逻辑"""
    
    document_loaded = pyqtSignal(str)  # 文档加载信号
    document_saved = pyqtSignal(str)   # 文档保存信号
    
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.recent_files = []  # 最近打开的文件列表
        self.max_recent_files = 5  # 最多保存的最近文件数量
        
    def new_document(self):
        """新建文档"""
        self.document.new_document()
        return True
        
    def open_document(self, parent_widget=None, file_path=None):
        """打开文档"""
        if file_path is None and parent_widget is not None:
            file_path, _ = QFileDialog.getOpenFileName(
                parent_widget, "打开文件", "", "绘图文件 (*.draw);;所有文件 (*)"
            )
            
        if file_path and os.path.exists(file_path):
            if self.document.load(file_path):
                self.add_recent_file(file_path)
                self.document_loaded.emit(file_path)
                return True
            else:
                if parent_widget:
                    QMessageBox.warning(parent_widget, "打开失败", "无法打开文件。")
        return False
        
    def save_document(self, parent_widget=None):
        """保存文档"""
        if not self.document.file_path:
            return self.save_document_as(parent_widget)
            
        if self.document.save(self.document.file_path):
            self.add_recent_file(self.document.file_path)
            self.document_saved.emit(self.document.file_path)
            return True
        else:
            if parent_widget:
                QMessageBox.warning(parent_widget, "保存失败", "无法保存文件。")
            return False
            
    def save_document_as(self, parent_widget=None):
        """另存为文档"""
        if parent_widget:
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget, "保存文件", "", "绘图文件 (*.draw);;所有文件 (*)"
            )
            
            if file_path:
                if not file_path.lower().endswith('.draw'):
                    file_path += ".draw"
                    
                if self.document.save(file_path):
                    self.add_recent_file(file_path)
                    self.document_saved.emit(file_path)
                    return True
                else:
                    QMessageBox.warning(parent_widget, "保存失败", "无法保存文件。")
        return False
        
    def export_image(self, parent_widget, canvas):
        """导出为图片"""
        if parent_widget:
            file_path, filter_type = QFileDialog.getSaveFileName(
                parent_widget, "导出图片", "", 
                "PNG图片 (*.png);;JPEG图片 (*.jpg);;BMP图片 (*.bmp);;所有文件 (*)"
            )
            
            if file_path:
                # 设置默认扩展名
                if "PNG" in filter_type and not file_path.lower().endswith('.png'):
                    file_path += ".png"
                elif "JPEG" in filter_type and not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                elif "BMP" in filter_type and not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                
                # 创建图像并渲染画布内容
                image = QImage(canvas.size(), QImage.Format_ARGB32)
                image.fill(QColor(255, 255, 255))
                
                painter = QPainter(image)
                canvas.render(painter)
                painter.end()
                
                if image.save(file_path):
                    QMessageBox.information(parent_widget, "导出成功", f"图片已导出到: {file_path}")
                    return True
                else:
                    QMessageBox.warning(parent_widget, "导出失败", "无法导出图片。")
        return False
        
    def add_recent_file(self, file_path):
        """添加最近文件"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            
        self.recent_files.insert(0, file_path)
        
        # 限制最近文件数量
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
            
    def get_recent_files(self):
        """获取最近文件列表"""
        # 过滤掉不存在的文件
        self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
        return self.recent_files
        
    def check_unsaved_changes(self, parent_widget):
        """检查是否有未保存的更改"""
        if not self.document.modified:
            return True
            
        reply = QMessageBox.question(
            parent_widget, "保存文档", 
            "文档已修改。\n是否保存修改？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            return self.save_document(parent_widget)
        elif reply == QMessageBox.Cancel:
            return False
            
        return True  # Discard 