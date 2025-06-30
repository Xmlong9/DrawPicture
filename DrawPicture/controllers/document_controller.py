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
            file_path, filter_type = QFileDialog.getSaveFileName(
                parent_widget, "保存文件", "", 
                "绘图文件 (*.draw);;PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg);;BMP图片 (*.bmp);;TIFF图片 (*.tiff);;WebP图片 (*.webp);;SVG图片 (*.svg);;所有文件 (*)"
            )
            
            if file_path:
                # 设置默认扩展名
                if "PNG" in filter_type and not file_path.lower().endswith('.png'):
                    file_path += ".png"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif "JPEG" in filter_type and not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif "BMP" in filter_type and not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif "TIFF" in filter_type and not file_path.lower().endswith('.tiff'):
                    file_path += ".tiff"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif "WebP" in filter_type and not file_path.lower().endswith('.webp'):
                    file_path += ".webp"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif "SVG" in filter_type and not file_path.lower().endswith('.svg'):
                    file_path += ".svg"
                    return self.export_image(parent_widget, parent_widget.canvas)
                elif not file_path.lower().endswith('.draw'):
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
        if parent_widget and canvas:
            file_path, filter_type = QFileDialog.getSaveFileName(
                parent_widget, "导出图片", "", 
                "PNG图片 (*.png);;JPEG图片 (*.jpg *.jpeg);;BMP图片 (*.bmp);;TIFF图片 (*.tiff);;WebP图片 (*.webp);;SVG图片 (*.svg);;ICO图标 (*.ico);;所有文件 (*)"
            )
            
            if file_path:
                # 设置默认扩展名
                if "PNG" in filter_type and not file_path.lower().endswith('.png'):
                    file_path += ".png"
                elif "JPEG" in filter_type and not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += ".jpg"
                elif "BMP" in filter_type and not file_path.lower().endswith('.bmp'):
                    file_path += ".bmp"
                elif "TIFF" in filter_type and not file_path.lower().endswith('.tiff'):
                    file_path += ".tiff"
                elif "WebP" in filter_type and not file_path.lower().endswith('.webp'):
                    file_path += ".webp"
                elif "SVG" in filter_type and not file_path.lower().endswith('.svg'):
                    file_path += ".svg"
                elif "ICO" in filter_type and not file_path.lower().endswith('.ico'):
                    file_path += ".ico"
                
                # 创建高分辨率图像
                canvas_size = canvas.size()
                scale_factor = 2.0  # 2倍分辨率
                image = QImage(canvas_size.width() * scale_factor, 
                             canvas_size.height() * scale_factor,
                             QImage.Format_ARGB32)
                image.fill(QColor(255, 255, 255))
                
                # 使用高质量渲染
                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.setRenderHint(QPainter.TextAntialiasing)
                
                # 应用缩放以提高分辨率
                painter.scale(scale_factor, scale_factor)
                canvas.render(painter)
                painter.end()
                
                # 根据文件类型设置保存选项
                save_options = {}
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    save_options['quality'] = 95  # JPEG质量设置（0-100）
                elif file_path.lower().endswith('.png'):
                    save_options['quality'] = 100  # PNG质量设置（0-100）
                    save_options['compression'] = 1  # PNG压缩级别（0-9）
                elif file_path.lower().endswith('.webp'):
                    save_options['quality'] = 95  # WebP质量设置（0-100）
                elif file_path.lower().endswith('.tiff'):
                    save_options['compression'] = 'lzw'  # TIFF压缩方式
                
                # 保存图片
                if image.save(file_path, quality=save_options.get('quality', -1)):
                    QMessageBox.information(parent_widget, "导出成功", 
                                         f"图片已导出到: {file_path}\n分辨率: {image.width()}x{image.height()}")
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