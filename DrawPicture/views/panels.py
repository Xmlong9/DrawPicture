#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QColorDialog, QSlider, QComboBox, QGroupBox, QListWidget,
                            QListWidgetItem, QSpinBox, QCheckBox, QToolButton, QMenu,
                            QAction, QInputDialog)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, pyqtSignal

class ToolPanel(QWidget):
    """工具面板"""
    
    tool_selected = pyqtSignal(str)  # 工具选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建工具按钮组
        tools_group = QGroupBox("工具")
        tools_layout = QVBoxLayout()
        
        # 创建工具按钮
        self.selection_btn = self._create_tool_button("选择", "selection")
        self.line_btn = self._create_tool_button("直线", "line")
        self.rectangle_btn = self._create_tool_button("矩形", "rectangle")
        self.circle_btn = self._create_tool_button("圆形", "circle")
        self.freehand_btn = self._create_tool_button("自由绘制", "freehand")
        self.spiral_btn = self._create_tool_button("螺线", "spiral")
        self.sine_btn = self._create_tool_button("正弦曲线", "sine")
        
        # 将按钮添加到布局
        tools_layout.addWidget(self.selection_btn)
        tools_layout.addWidget(self.line_btn)
        tools_layout.addWidget(self.rectangle_btn)
        tools_layout.addWidget(self.circle_btn)
        tools_layout.addWidget(self.freehand_btn)
        tools_layout.addWidget(self.spiral_btn)
        tools_layout.addWidget(self.sine_btn)
        tools_layout.addStretch(1)
        
        tools_group.setLayout(tools_layout)
        
        # 将工具组添加到主布局
        layout.addWidget(tools_group)
        layout.addStretch(1)
        
        # 默认选择选择工具
        self.selection_btn.setChecked(True)
        self.current_tool = "selection"
        
    def _create_tool_button(self, text, tool_name):
        """创建工具按钮"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda checked, t=tool_name: self._on_tool_clicked(t))
        return button
        
    def _on_tool_clicked(self, tool_name):
        """工具按钮点击处理"""
        # 清除所有按钮的选中状态
        for btn in [self.selection_btn, self.line_btn, self.rectangle_btn, 
                  self.circle_btn, self.freehand_btn, self.spiral_btn, self.sine_btn]:
            btn.setChecked(False)
            
        # 设置当前工具
        self.current_tool = tool_name
        
        # 设置当前按钮选中
        if tool_name == "selection":
            self.selection_btn.setChecked(True)
        elif tool_name == "line":
            self.line_btn.setChecked(True)
        elif tool_name == "rectangle":
            self.rectangle_btn.setChecked(True)
        elif tool_name == "circle":
            self.circle_btn.setChecked(True)
        elif tool_name == "freehand":
            self.freehand_btn.setChecked(True)
        elif tool_name == "spiral":
            self.spiral_btn.setChecked(True)
        elif tool_name == "sine":
            self.sine_btn.setChecked(True)
            
        # 发送信号
        self.tool_selected.emit(tool_name)
        
    def select_tool(self, tool_name):
        """外部调用，选择工具"""
        self._on_tool_clicked(tool_name)


class ColorPanel(QWidget):
    """颜色面板"""
    
    color_changed = pyqtSignal(QColor, bool)  # 颜色变化信号，参数：颜色，是否是填充色
    line_width_changed = pyqtSignal(int)  # 线宽变化信号
    line_style_changed = pyqtSignal(int)  # 线型变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pen_color = QColor(0, 0, 0)  # 默认黑色线条
        self.fill_color = QColor(0, 0, 0, 0)  # 默认透明填充
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建颜色选择组
        color_group = QGroupBox("颜色")
        color_layout = QVBoxLayout()
        
        # 线条颜色选择器
        pen_layout = QHBoxLayout()
        pen_layout.addWidget(QLabel("线条:"))
        self.pen_color_btn = QPushButton()
        self.pen_color_btn.setFixedSize(30, 30)
        self._update_color_button(self.pen_color_btn, self.pen_color)
        self.pen_color_btn.clicked.connect(self._on_pen_color_clicked)
        pen_layout.addWidget(self.pen_color_btn)
        color_layout.addLayout(pen_layout)
        
        # 填充颜色选择器
        fill_layout = QHBoxLayout()
        fill_layout.addWidget(QLabel("填充:"))
        self.fill_color_btn = QPushButton()
        self.fill_color_btn.setFixedSize(30, 30)
        self._update_color_button(self.fill_color_btn, self.fill_color)
        self.fill_color_btn.clicked.connect(self._on_fill_color_clicked)
        fill_layout.addWidget(self.fill_color_btn)
        color_layout.addLayout(fill_layout)
        
        # 预定义颜色列表
        predefined_layout = QHBoxLayout()
        self.predefined_colors = [
            QColor(0, 0, 0),       # 黑色
            QColor(255, 255, 255), # 白色
            QColor(255, 0, 0),     # 红色
            QColor(0, 255, 0),     # 绿色
            QColor(0, 0, 255),     # 蓝色
            QColor(255, 255, 0),   # 黄色
            QColor(0, 255, 255),   # 青色
            QColor(255, 0, 255),   # 洋红
        ]
        
        for color in self.predefined_colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(20, 20)
            self._update_color_button(color_btn, color)
            color_btn.clicked.connect(lambda checked, c=color: self._on_predefined_color_clicked(c))
            predefined_layout.addWidget(color_btn)
            
        color_layout.addLayout(predefined_layout)
        
        # 线宽选择
        line_width_layout = QHBoxLayout()
        line_width_layout.addWidget(QLabel("线宽:"))
        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setRange(1, 20)
        self.line_width_slider.setValue(2)
        self.line_width_slider.setTickPosition(QSlider.TicksBelow)
        self.line_width_slider.setTickInterval(2)
        self.line_width_slider.valueChanged.connect(self._on_line_width_changed)
        line_width_layout.addWidget(self.line_width_slider)
        self.line_width_label = QLabel("2")
        line_width_layout.addWidget(self.line_width_label)
        color_layout.addLayout(line_width_layout)
        
        # 线型选择
        line_style_layout = QHBoxLayout()
        line_style_layout.addWidget(QLabel("线型:"))
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItem("实线", Qt.SolidLine)
        self.line_style_combo.addItem("虚线", Qt.DashLine)
        self.line_style_combo.addItem("点线", Qt.DotLine)
        self.line_style_combo.addItem("点虚线", Qt.DashDotLine)
        self.line_style_combo.currentIndexChanged.connect(self._on_line_style_changed)
        line_style_layout.addWidget(self.line_style_combo)
        color_layout.addLayout(line_style_layout)
        
        color_group.setLayout(color_layout)
        
        # 将颜色组添加到主布局
        layout.addWidget(color_group)
        layout.addStretch(1)
        
    def _update_color_button(self, button, color):
        """更新颜色按钮样式"""
        pixmap = QPixmap(button.size())
        pixmap.fill(color)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(button.size())
        
    def _on_pen_color_clicked(self):
        """线条颜色按钮点击处理"""
        color = QColorDialog.getColor(self.pen_color, self, "选择线条颜色",
                                    QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.pen_color = color
            self._update_color_button(self.pen_color_btn, color)
            self.color_changed.emit(color, False)  # 发送颜色变化信号，不是填充色
            
    def _on_fill_color_clicked(self):
        """填充颜色按钮点击处理"""
        color = QColorDialog.getColor(self.fill_color, self, "选择填充颜色",
                                    QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.fill_color = color
            self._update_color_button(self.fill_color_btn, color)
            self.color_changed.emit(color, True)  # 发送颜色变化信号，是填充色
            print(f"设置填充颜色: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")
            
    def _on_predefined_color_clicked(self, color):
        """预定义颜色按钮点击处理"""
        self.pen_color = color
        self._update_color_button(self.pen_color_btn, color)
        self.color_changed.emit(color, False)  # 发送颜色变化信号，不是填充色
        
    def _on_line_width_changed(self, value):
        """线宽变化处理"""
        self.line_width_label.setText(str(value))
        self.line_width_changed.emit(value)
        
    def _on_line_style_changed(self, index):
        """线型变化处理"""
        style = self.line_style_combo.itemData(index)
        self.line_style_changed.emit(style)
        

class LayerPanel(QWidget):
    """图层面板"""
    
    layer_selected = pyqtSignal(int)  # 图层选择信号
    layer_visibility_changed = pyqtSignal(int, bool)  # 图层可见性变化信号
    
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.init_ui()
        
        # 绑定文档信号
        self.document.document_changed.connect(self.update_layer_list)
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建图层列表组
        layers_group = QGroupBox("图层")
        layers_layout = QVBoxLayout()
        
        # 图层列表
        self.layer_list = QListWidget()
        self.layer_list.itemClicked.connect(self._on_layer_clicked)
        layers_layout.addWidget(self.layer_list)
        
        # 图层操作按钮
        buttons_layout = QHBoxLayout()
        
        self.add_layer_btn = QPushButton("添加")
        self.add_layer_btn.clicked.connect(self._on_add_layer)
        buttons_layout.addWidget(self.add_layer_btn)
        
        self.rename_layer_btn = QPushButton("重命名")
        self.rename_layer_btn.clicked.connect(self._on_rename_layer)
        buttons_layout.addWidget(self.rename_layer_btn)
        
        self.delete_layer_btn = QPushButton("删除")
        self.delete_layer_btn.clicked.connect(self._on_delete_layer)
        buttons_layout.addWidget(self.delete_layer_btn)
        
        layers_layout.addLayout(buttons_layout)
        
        layers_group.setLayout(layers_layout)
        
        # 将图层组添加到主布局
        layout.addWidget(layers_group)
        layout.addStretch(1)
        
        # 初始化图层列表
        self.update_layer_list()
        
    def update_layer_list(self):
        """更新图层列表"""
        self.layer_list.clear()
        
        for i, layer in enumerate(self.document.layers):
            item = QListWidgetItem(layer['name'])
            item.setData(Qt.UserRole, i)  # 存储图层索引
            
            # 如果是当前选中的图层，设置为选中状态
            if i == self.document.current_layer:
                item.setSelected(True)
                self.layer_list.setCurrentItem(item)
                
            # 添加可见性复选框
            check_box = QCheckBox()
            check_box.setChecked(layer['visible'])
            check_box.stateChanged.connect(lambda state, idx=i: self._on_layer_visibility_changed(idx, state))
            
            # 将项目添加到列表
            self.layer_list.addItem(item)
            
            # 设置项目的小部件
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(check_box)
            layout.addStretch()
            layout.setContentsMargins(5, 2, 5, 2)
            widget.setLayout(layout)
            
            self.layer_list.setItemWidget(item, widget)
            
    def _on_layer_clicked(self, item):
        """图层点击处理"""
        layer_index = item.data(Qt.UserRole)
        self.document.select_layer(layer_index)
        self.layer_selected.emit(layer_index)
        
    def _on_layer_visibility_changed(self, layer_index, state):
        """图层可见性变化处理"""
        visible = state == Qt.Checked
        self.document.set_layer_visibility(layer_index, visible)
        self.layer_visibility_changed.emit(layer_index, visible)
        
    def _on_add_layer(self):
        """添加图层"""
        name, ok = QInputDialog.getText(self, "添加图层", "图层名称:")
        if ok and name:
            self.document.add_layer(name)
            self.update_layer_list()
            
    def _on_rename_layer(self):
        """重命名图层"""
        current_item = self.layer_list.currentItem()
        if current_item:
            layer_index = current_item.data(Qt.UserRole)
            old_name = self.document.layers[layer_index]['name']
            name, ok = QInputDialog.getText(self, "重命名图层", "图层名称:", text=old_name)
            if ok and name:
                self.document.rename_layer(layer_index, name)
                self.update_layer_list()
                
    def _on_delete_layer(self):
        """删除图层"""
        current_item = self.layer_list.currentItem()
        if current_item:
            layer_index = current_item.data(Qt.UserRole)
            if layer_index > 0:  # 不删除默认图层
                self.document.remove_layer(layer_index)
                self.update_layer_list() 