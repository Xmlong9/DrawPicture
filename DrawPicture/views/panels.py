#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QColorDialog, QSlider, QComboBox, QGroupBox, QListWidget,
                            QListWidgetItem, QSpinBox, QCheckBox, QToolButton, QMenu,
    QAction, QInputDialog, QGridLayout, QFormLayout, QMessageBox,
    QLineEdit, QAbstractItemView, QScrollArea, QSizePolicy, QFrame,
    QTabWidget, QRadioButton, QButtonGroup, QDialog
)
from PyQt5.QtGui import (
    QIcon, QColor, QPainter, QPixmap, QPen, QBrush, QPalette,
    QLinearGradient, QRadialGradient, QGradient
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer

from DrawPicture.models.document import DrawingDocument
from DrawPicture.models.tools import ToolType

class ToolPanel(QWidget):
    """工具面板"""
    
    tool_selected = pyqtSignal(str)  # 工具选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建工具按钮组
        tools_group = QGroupBox("工具箱")
        tools_group.setMinimumWidth(120)  # 设置最小宽度
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(8)
        tools_layout.setContentsMargins(10, 15, 10, 10)  # 增加内边距
        
        # 创建工具按钮并添加图标
        self.selection_btn = self._create_tool_button("选择", "selection", "⬚")
        self.pan_btn = self._create_tool_button("平移", "pan", "✋")
        self.line_btn = self._create_tool_button("直线", "line", "╱")
        self.rectangle_btn = self._create_tool_button("矩形", "rectangle", "□")
        self.circle_btn = self._create_tool_button("圆形", "circle", "○")
        self.freehand_btn = self._create_tool_button("自由绘制", "freehand", "✎")
        self.spiral_btn = self._create_tool_button("螺线", "spiral", "@")
        self.sine_btn = self._create_tool_button("正弦曲线", "sine", "~")
        self.eraser_btn = self._create_tool_button("橡皮擦", "eraser", "☒")
        
        # 将按钮添加到布局
        tools_layout.addWidget(self.selection_btn)
        tools_layout.addWidget(self.pan_btn)
        tools_layout.addWidget(self.line_btn)
        tools_layout.addWidget(self.rectangle_btn)
        tools_layout.addWidget(self.circle_btn)
        tools_layout.addWidget(self.freehand_btn)
        tools_layout.addWidget(self.spiral_btn)
        tools_layout.addWidget(self.sine_btn)
        tools_layout.addWidget(self.eraser_btn)
        tools_layout.addStretch(1)
        
        tools_group.setLayout(tools_layout)
        
        # 将工具组添加到主布局
        layout.addWidget(tools_group)
        layout.addStretch(1)
        
        # 默认选择选择工具
        self.selection_btn.setChecked(True)
        self.current_tool = "selection"
        
    def _create_tool_button(self, text, tool_name, icon_text=""):
        """创建工具按钮"""
        button = QPushButton()
        button.setCheckable(True)
        button.setFixedHeight(36)
        
        # 创建图标
        if icon_text:
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(Qt.black, 2))
            
            # 绘制图标文本
            font = painter.font()
            font.setPointSize(16)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, icon_text)
            
            painter.end()
            
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(24, 24))
        
        # 设置文本和布局
        button.setText(text)
        button.setToolTip(f"{text}工具")
        
        # 连接信号
        button.clicked.connect(lambda checked, t=tool_name: self._on_tool_clicked(t))
        
        return button
        
    def _on_tool_clicked(self, tool_name):
        """工具按钮点击处理"""
        # 清除所有按钮的选中状态
        for btn in [self.selection_btn, self.pan_btn, self.line_btn, self.rectangle_btn, 
                  self.circle_btn, self.freehand_btn, self.spiral_btn, self.sine_btn,
                  self.eraser_btn]:  # 包含所有工具按钮
            btn.setChecked(False)
            
        # 设置当前工具
        self.current_tool = tool_name
        
        # 设置当前按钮选中
        if tool_name == "selection":
            self.selection_btn.setChecked(True)
        elif tool_name == "pan":
            self.pan_btn.setChecked(True)
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
        elif tool_name == "eraser":
            self.eraser_btn.setChecked(True)  # 设置橡皮擦按钮选中状态
            
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
    eraser_size_changed = pyqtSignal(int)  # 橡皮擦大小变化信号
    gradient_changed = pyqtSignal(QColor, QColor, int, int)  # 渐变色变化信号：起始颜色，结束颜色，类型，方向
    gradient_pen_changed = pyqtSignal(QColor, QColor, int, int)  # 线条渐变色变化信号：起始颜色，结束颜色，类型，方向
    
    def __init__(self, parent=None):
        """初始化颜色面板"""
        super().__init__(parent)
        
        # 颜色相关属性
        self.pen_color = QColor(0, 0, 0, 255)  # 默认线条颜色：黑色
        self.fill_color = QColor(255, 255, 255, 255)  # 默认填充颜色：白色
        self.eraser_size = 20  # 默认橡皮擦大小
        self.current_tool = "selection"  # 当前选中的工具
        
        # 渐变相关属性
        self.gradient_start_color = QColor(255, 255, 0)  # 默认渐变起始颜色：黄色
        self.gradient_end_color = QColor(0, 255, 0)  # 默认渐变结束颜色：绿色
        self.gradient_type = 0  # 0: 线性渐变, 1: 径向渐变
        self.gradient_direction = 0  # 0: 水平, 1: 垂直, 2: 对角线
        
        # 当前选中的颜色按钮（用于预定义颜色选择）
        self.current_color_button = None
        
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
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # 减少间距
        layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        
        # 创建颜色选择组
        color_group = QGroupBox("颜色与样式")
        color_group.setMinimumWidth(100)  # 减小最小宽度
        color_layout = QVBoxLayout()
        color_layout.setSpacing(5)  # 减少间距
        color_layout.setContentsMargins(5, 10, 5, 5)  # 减少内边距
        
        # 创建选项卡控件，分为"基本颜色"和"渐变色"两个选项卡
        tab_widget = QTabWidget()
        tab_widget.setMaximumHeight(300)  # 限制最大高度
        
        # 基本颜色选项卡
        basic_color_tab = QWidget()
        basic_color_layout = QVBoxLayout(basic_color_tab)
        basic_color_layout.setSpacing(5)  # 减少间距
        basic_color_layout.setContentsMargins(3, 3, 3, 3)  # 减少内边距
        
        # 颜色选择器区域
        color_selector_layout = QHBoxLayout()
        color_selector_layout.setSpacing(3)  # 减少间距
        
        # 线条颜色选择器
        pen_layout = QVBoxLayout()
        pen_layout.setSpacing(2)  # 减少间距
        pen_layout.setAlignment(Qt.AlignCenter)
        pen_label = QLabel("线条颜色")
        pen_label.setAlignment(Qt.AlignCenter)
        pen_layout.addWidget(pen_label)
        
        self.pen_color_btn = QPushButton()
        self.pen_color_btn.setFixedSize(30, 30)  # 减小按钮大小
        self.pen_color_btn.setCursor(Qt.PointingHandCursor)
        self._update_color_button(self.pen_color_btn, self.pen_color)
        self.pen_color_btn.clicked.connect(self._on_pen_color_clicked)
        self.pen_color_btn.setToolTip("点击选择线条颜色")
        pen_layout.addWidget(self.pen_color_btn)
        color_selector_layout.addLayout(pen_layout)
        
        # 分隔线
        line = QWidget()
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: #c0c0c0;")
        color_selector_layout.addWidget(line)
        
        # 填充颜色选择器
        fill_layout = QVBoxLayout()
        fill_layout.setSpacing(2)  # 减少间距
        fill_layout.setAlignment(Qt.AlignCenter)
        fill_label = QLabel("填充颜色")
        fill_label.setAlignment(Qt.AlignCenter)
        fill_layout.addWidget(fill_label)
        
        self.fill_color_btn = QPushButton()
        self.fill_color_btn.setFixedSize(30, 30)  # 减小按钮大小
        self.fill_color_btn.setCursor(Qt.PointingHandCursor)
        self._update_color_button(self.fill_color_btn, self.fill_color)
        self.fill_color_btn.clicked.connect(self._on_fill_color_clicked)
        self.fill_color_btn.setToolTip("点击选择填充颜色")
        fill_layout.addWidget(self.fill_color_btn)
        color_selector_layout.addLayout(fill_layout)
        
        basic_color_layout.addLayout(color_selector_layout)
        
        # 分隔线
        h_line = QWidget()
        h_line.setFixedHeight(1)
        h_line.setStyleSheet("background-color: #c0c0c0;")
        basic_color_layout.addWidget(h_line)
        
        # 预定义颜色调色板
        palette_label = QLabel("调色板")
        palette_label.setAlignment(Qt.AlignCenter)
        basic_color_layout.addWidget(palette_label)
        
        # 预定义颜色列表 - 紧凑布局
        predefined_layout = QGridLayout()
        predefined_layout.setSpacing(2)  # 减少间距
        self.predefined_colors = [
            QColor(0, 0, 0),       # 黑色
            QColor(128, 128, 128), # 灰色
            QColor(255, 255, 255), # 白色
            QColor(255, 0, 0),     # 红色
            QColor(255, 165, 0),   # 橙色
            QColor(255, 255, 0),   # 黄色
            QColor(0, 255, 0),     # 绿色
            QColor(0, 255, 255),   # 青色
            QColor(0, 0, 255),     # 蓝色
            QColor(128, 0, 128),   # 紫色
            QColor(255, 0, 255),   # 洋红
            QColor(165, 42, 42),   # 棕色
        ]
        
        row, col = 0, 0
        for color in self.predefined_colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(18, 18)  # 减小颜色按钮大小
            color_btn.setCursor(Qt.PointingHandCursor)
            self._update_color_button(color_btn, color)
            color_btn.clicked.connect(lambda checked, c=color: self._on_predefined_color_clicked(c))
            
            # 设置工具提示显示颜色值
            r, g, b, a = color.getRgb()
            color_btn.setToolTip(f"RGB: {r},{g},{b}")
            
            predefined_layout.addWidget(color_btn, row, col)
            col += 1
            if col > 3:  # 4列布局
                col = 0
                row += 1
            
        basic_color_layout.addLayout(predefined_layout)
        
        # 添加基本颜色选项卡
        tab_widget.addTab(basic_color_tab, "基本颜色")
        
        # 渐变色选项卡
        gradient_tab = QWidget()
        gradient_layout = QVBoxLayout(gradient_tab)
        gradient_layout.setSpacing(5)  # 减少间距
        gradient_layout.setContentsMargins(3, 3, 3, 3)  # 减少内边距
        
        # 渐变色预览区域
        gradient_preview_label = QLabel("渐变预览")
        gradient_preview_label.setAlignment(Qt.AlignCenter)
        gradient_layout.addWidget(gradient_preview_label)
        
        self.gradient_preview = QPushButton()
        self.gradient_preview.setFixedSize(120, 40)  # 减小预览尺寸
        self.gradient_preview.setEnabled(False)  # 禁用点击
        gradient_layout.addWidget(self.gradient_preview, 0, Qt.AlignCenter)
        
        # 渐变色起点和终点选择
        gradient_colors_layout = QHBoxLayout()
        gradient_colors_layout.setSpacing(5)  # 减少间距
        
        # 起点颜色
        start_color_layout = QVBoxLayout()
        start_color_layout.setSpacing(2)  # 减少间距
        start_color_layout.setAlignment(Qt.AlignCenter)
        start_color_label = QLabel("起始颜色")
        start_color_label.setAlignment(Qt.AlignCenter)
        start_color_layout.addWidget(start_color_label)
        
        self.gradient_start_btn = QPushButton()
        self.gradient_start_btn.setFixedSize(25, 25)  # 减小按钮大小
        self.gradient_start_btn.setCursor(Qt.PointingHandCursor)
        self._update_color_button(self.gradient_start_btn, self.gradient_start_color)
        self.gradient_start_btn.clicked.connect(self._on_gradient_start_clicked)
        start_color_layout.addWidget(self.gradient_start_btn)
        gradient_colors_layout.addLayout(start_color_layout)
        
        # 终点颜色
        end_color_layout = QVBoxLayout()
        end_color_layout.setSpacing(2)  # 减少间距
        end_color_layout.setAlignment(Qt.AlignCenter)
        end_label = QLabel("结束颜色")
        end_label.setAlignment(Qt.AlignCenter)
        end_color_layout.addWidget(end_label)
        
        self.gradient_end_btn = QPushButton()
        self.gradient_end_btn.setFixedSize(25, 25)  # 减小按钮大小
        self.gradient_end_btn.setCursor(Qt.PointingHandCursor)
        self._update_color_button(self.gradient_end_btn, self.gradient_end_color)
        self.gradient_end_btn.clicked.connect(self._on_gradient_end_clicked)
        end_color_layout.addWidget(self.gradient_end_btn)
        gradient_colors_layout.addLayout(end_color_layout)
        
        gradient_layout.addLayout(gradient_colors_layout)
        
        # 分隔线
        h_line2 = QWidget()
        h_line2.setFixedHeight(1)
        h_line2.setStyleSheet("background-color: #c0c0c0;")
        gradient_layout.addWidget(h_line2)
        
        # 渐变类型和方向选择 - 使用更紧凑的布局
        types_layout = QHBoxLayout()
        types_layout.setSpacing(3)  # 减少间距
        
        # 渐变类型选择
        type_layout = QVBoxLayout()
        type_layout.setSpacing(2)  # 减少间距
        
        type_label = QLabel("渐变类型")
        type_label.setAlignment(Qt.AlignCenter)
        type_layout.addWidget(type_label)
        
        gradient_type_layout = QHBoxLayout()
        gradient_type_layout.setSpacing(2)  # 减少间距
        self.gradient_type_group = QButtonGroup(self)
        
        self.linear_gradient_radio = QRadioButton("线性")  # 简化标签文本
        self.linear_gradient_radio.setChecked(True)
        self.linear_gradient_radio.clicked.connect(self._on_gradient_type_changed)
        self.gradient_type_group.addButton(self.linear_gradient_radio, 0)
        gradient_type_layout.addWidget(self.linear_gradient_radio)
        
        self.radial_gradient_radio = QRadioButton("径向")  # 简化标签文本
        self.radial_gradient_radio.clicked.connect(self._on_gradient_type_changed)
        self.gradient_type_group.addButton(self.radial_gradient_radio, 1)
        gradient_type_layout.addWidget(self.radial_gradient_radio)
        
        type_layout.addLayout(gradient_type_layout)
        types_layout.addLayout(type_layout)
        
        gradient_layout.addLayout(types_layout)
        
        # 线性渐变方向选择（只有在线性渐变时才显示）
        self.direction_widget = QWidget()
        direction_layout = QVBoxLayout(self.direction_widget)
        direction_layout.setSpacing(2)  # 减少间距
        direction_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        direction_label = QLabel("渐变方向")
        direction_label.setAlignment(Qt.AlignCenter)
        direction_layout.addWidget(direction_label)
        
        direction_buttons_layout = QHBoxLayout()
        direction_buttons_layout.setSpacing(2)  # 减少间距
        self.direction_group = QButtonGroup(self)
        
        self.horizontal_radio = QRadioButton("水平")
        self.horizontal_radio.setChecked(True)
        self.horizontal_radio.clicked.connect(self._on_gradient_direction_changed)
        self.direction_group.addButton(self.horizontal_radio, 0)
        direction_buttons_layout.addWidget(self.horizontal_radio)
        
        self.vertical_radio = QRadioButton("垂直")
        self.vertical_radio.clicked.connect(self._on_gradient_direction_changed)
        self.direction_group.addButton(self.vertical_radio, 1)
        direction_buttons_layout.addWidget(self.vertical_radio)
        
        self.diagonal_radio = QRadioButton("对角")  # 简化标签文本
        self.diagonal_radio.clicked.connect(self._on_gradient_direction_changed)
        self.direction_group.addButton(self.diagonal_radio, 2)
        direction_buttons_layout.addWidget(self.diagonal_radio)
        
        direction_layout.addLayout(direction_buttons_layout)
        gradient_layout.addWidget(self.direction_widget)
        
        # 应用和取消渐变按钮 - 放在同一行
        gradient_buttons_layout = QHBoxLayout()
        gradient_buttons_layout.setSpacing(3)  # 减少间距
        
        self.apply_gradient_btn = QPushButton("应用渐变")  # 简化标签文本
        self.apply_gradient_btn.setFixedHeight(25)  # 减小按钮高度
        self.apply_gradient_btn.clicked.connect(self._on_apply_gradient)
        gradient_buttons_layout.addWidget(self.apply_gradient_btn)
        
        self.disable_gradient_btn = QPushButton("取消渐变")  # 简化标签文本
        self.disable_gradient_btn.setFixedHeight(25)  # 减小按钮高度
        self.disable_gradient_btn.clicked.connect(self._on_disable_gradient)
        gradient_buttons_layout.addWidget(self.disable_gradient_btn)
        
        gradient_layout.addLayout(gradient_buttons_layout)
        
        # 添加渐变色选项卡
        tab_widget.addTab(gradient_tab, "渐变色")
        
        # 将选项卡添加到颜色布局
        color_layout.addWidget(tab_widget)
        
        # 分隔线
        h_line3 = QWidget()
        h_line3.setFixedHeight(1)
        h_line3.setStyleSheet("background-color: #c0c0c0;")
        color_layout.addWidget(h_line3)
        
        # 线宽和线型选择 - 更紧凑的布局
        style_layout = QHBoxLayout()
        style_layout.setSpacing(5)  # 减少间距
        
        # 线宽选择
        line_width_layout = QVBoxLayout()
        line_width_layout.setSpacing(2)  # 减少间距
        line_width_header = QHBoxLayout()
        line_width_header.setSpacing(2)  # 减少间距
        line_width_header.addWidget(QLabel("线宽:"))
        self.line_width_label = QLabel("2")
        self.line_width_label.setAlignment(Qt.AlignRight)
        line_width_header.addWidget(self.line_width_label)
        line_width_layout.addLayout(line_width_header)
        
        self.line_width_slider = QSlider(Qt.Horizontal)
        self.line_width_slider.setFixedHeight(20)  # 减小滑块高度
        self.line_width_slider.setRange(1, 20)
        self.line_width_slider.setValue(2)
        self.line_width_slider.setTickPosition(QSlider.TicksBelow)
        self.line_width_slider.setTickInterval(5)  # 增大刻度间隔
        self.line_width_slider.valueChanged.connect(self._on_line_width_changed)
        line_width_layout.addWidget(self.line_width_slider)
        style_layout.addLayout(line_width_layout)
        
        # 线型选择
        line_style_layout = QVBoxLayout()
        line_style_layout.setSpacing(2)  # 减少间距
        line_style_layout.addWidget(QLabel("线型:"))
        self.line_style_combo = QComboBox()
        self.line_style_combo.setFixedHeight(22)  # 减小下拉框高度
        self.line_style_combo.addItem("实线", Qt.SolidLine)
        self.line_style_combo.addItem("虚线", Qt.DashLine)
        self.line_style_combo.addItem("点线", Qt.DotLine)
        self.line_style_combo.addItem("点虚线", Qt.DashDotLine)
        self.line_style_combo.currentIndexChanged.connect(self._on_line_style_changed)
        line_style_layout.addWidget(self.line_style_combo)
        style_layout.addLayout(line_style_layout)
        
        color_layout.addLayout(style_layout)
        
        # 橡皮擦大小选择（默认隐藏）
        self.eraser_size_widget = QWidget()
        eraser_size_layout = QVBoxLayout(self.eraser_size_widget)
        eraser_size_layout.setContentsMargins(0, 0, 0, 0)
        eraser_size_layout.setSpacing(2)  # 减少间距
        
        eraser_header = QHBoxLayout()
        eraser_header.setSpacing(2)  # 减少间距
        eraser_header.addWidget(QLabel("橡皮擦大小:"))
        self.eraser_size_label = QLabel(str(self.eraser_size))
        self.eraser_size_label.setAlignment(Qt.AlignRight)
        eraser_header.addWidget(self.eraser_size_label)
        eraser_size_layout.addLayout(eraser_header)
        
        self.eraser_size_slider = QSlider(Qt.Horizontal)
        self.eraser_size_slider.setFixedHeight(20)  # 减小滑块高度
        self.eraser_size_slider.setRange(5, 50)
        self.eraser_size_slider.setValue(self.eraser_size)
        self.eraser_size_slider.setTickPosition(QSlider.TicksBelow)
        self.eraser_size_slider.setTickInterval(10)  # 增大刻度间隔
        self.eraser_size_slider.valueChanged.connect(self._on_eraser_size_changed)
        eraser_size_layout.addWidget(self.eraser_size_slider)
        
        color_layout.addWidget(self.eraser_size_widget)
        self.eraser_size_widget.hide()  # 默认隐藏
        
        color_group.setLayout(color_layout)
        
        # 将颜色组添加到主布局
        layout.addWidget(color_group)
        layout.addStretch(1)
        
        # 初始化渐变预览
        self._update_gradient_preview()
        
    def _update_color_button(self, button, color):
        """更新颜色按钮样式"""
        # 创建一个新的pixmap
        pixmap = QPixmap(button.size())
        pixmap.fill(Qt.transparent)
        
        # 创建painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制颜色区域（带圆角和边框）
        painter.setPen(QPen(Qt.gray, 1))
        
        # 如果是透明色，绘制特殊标记
        if color.alpha() == 0:
            # 绘制透明背景格子
            bg_brush = QBrush(QColor(230, 230, 230))
            painter.setBrush(bg_brush)
            painter.drawRoundedRect(0, 0, pixmap.width() - 1, pixmap.height() - 1, 4, 4)
            
            # 绘制红色斜线表示透明
            painter.setPen(QPen(Qt.red, 2))
            painter.drawLine(0, pixmap.height() - 1, pixmap.width() - 1, 0)
        else:
            # 普通颜色
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(0, 0, pixmap.width() - 1, pixmap.height() - 1, 4, 4)
        
        painter.end()
        
        # 设置按钮图标
        button.setIcon(QIcon(pixmap))
        button.setIconSize(button.size())
        
    def _on_pen_color_clicked(self):
        """线条颜色按钮点击处理"""
        # 设置当前颜色按钮
        self.current_color_button = self.pen_color_btn
        
        # 创建自定义颜色对话框
        dialog = QColorDialog(self.pen_color, self)
        dialog.setWindowTitle("选择线条颜色")
        dialog.setOption(QColorDialog.ShowAlphaChannel)
        
        # 添加渐变色选择按钮
        gradient_button = QPushButton("使用渐变色", dialog)
        gradient_button.clicked.connect(lambda: self._show_gradient_dialog(is_fill=False))
        
        # 将按钮添加到对话框布局中
        layout = dialog.layout()
        if layout:
            # 检查布局类型，根据不同类型添加按钮
            if isinstance(layout, QGridLayout):
                layout.addWidget(gradient_button, layout.rowCount(), 0, 1, layout.columnCount())
            else:
                layout.addWidget(gradient_button)
        
        # 显示对话框
        if dialog.exec_():
            color = dialog.selectedColor()
            if color.isValid():
                self.pen_color = color
                self._update_color_button(self.pen_color_btn, color)
                self.color_changed.emit(color, False)  # False表示不是填充颜色
            
    def _on_fill_color_clicked(self):
        """填充颜色按钮点击处理"""
        # 设置当前颜色按钮
        self.current_color_button = self.fill_color_btn
        
        # 获取当前填充颜色，如果是透明的，则创建一个不透明版本作为默认选择
        current_color = self.fill_color
        if current_color.alpha() == 0:
            # 创建不透明版本的颜色（保持RGB值，但设置alpha为255）
            current_color = QColor(current_color.red(), current_color.green(), current_color.blue(), 255)
        
        # 创建自定义颜色对话框
        dialog = QColorDialog(current_color, self)
        dialog.setWindowTitle("选择填充颜色")
        dialog.setOption(QColorDialog.ShowAlphaChannel)
        
        # 添加渐变色选择按钮
        gradient_button = QPushButton("使用渐变色", dialog)
        gradient_button.clicked.connect(lambda: self._show_gradient_dialog(is_fill=True))
        
        # 将按钮添加到对话框布局中
        layout = dialog.layout()
        if layout:
            # 检查布局类型，根据不同类型添加按钮
            if isinstance(layout, QGridLayout):
                layout.addWidget(gradient_button, layout.rowCount(), 0, 1, layout.columnCount())
            else:
                layout.addWidget(gradient_button)
        
        # 显示对话框
        if dialog.exec_():
            color = dialog.selectedColor()
            if color.isValid():
                self.fill_color = color
                self._update_color_button(self.fill_color_btn, color)
                self.color_changed.emit(color, True)  # 发送颜色变化信号，是填充色
    
    def _on_gradient_changed(self, start_color, end_color, gradient_type, direction):
        """渐变色变化处理"""
        # 检查是否是线条渐变或填充渐变
        sender = self.sender()
        is_pen_gradient = hasattr(sender, 'objectName') and sender.objectName() == 'gradient_pen_dialog'
        
        # 保存渐变设置到实例变量
        if is_pen_gradient:
            # 线条渐变
            self.gradient_pen_start_color = start_color
            self.gradient_pen_end_color = end_color
            self.gradient_pen_type = gradient_type
            self.gradient_pen_direction = direction
            # 发送渐变色变化信号
            self.gradient_pen_changed.emit(start_color, end_color, gradient_type, direction)
            
            # 更新预览（如果有线条渐变预览）
            if hasattr(self, '_update_gradient_pen_preview'):
                self._update_gradient_pen_preview()
        else:
            # 填充渐变
            self.gradient_start_color = start_color
            self.gradient_end_color = end_color
            self.gradient_type = gradient_type
            self.gradient_direction = direction
            # 发送渐变色变化信号
            self.gradient_changed.emit(start_color, end_color, gradient_type, direction)

    def _show_gradient_dialog(self, is_fill=True):
        """显示渐变色选择对话框"""
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择渐变色")
        dialog.setMinimumWidth(350)
        dialog.setMinimumHeight(400)
        
        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f8f8;
                border: 1px solid #dcdcdc;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QRadioButton {
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        
        # 设置对话框对象名称以区分线条渐变和填充渐变
        if is_fill:
            dialog.setObjectName("gradient_fill_dialog")
        else:
            dialog.setObjectName("gradient_pen_dialog")
        
        # 创建对话框布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 渐变色预览区域
        preview_label = QLabel("渐变预览")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(preview_label)
        
        preview = QPushButton()
        preview.setFixedSize(300, 60)
        preview.setEnabled(False)  # 禁用点击
        preview.setStyleSheet("border: 1px solid #a0a0a0; border-radius: 6px;")
        layout.addWidget(preview, 0, Qt.AlignCenter)
        
        # 渐变色起点和终点选择
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(30)  # 增加间距
        
        # 起点颜色
        start_color_layout = QVBoxLayout()
        start_color_layout.setAlignment(Qt.AlignCenter)
        start_color_layout.setSpacing(8)
        start_color_label = QLabel("起始颜色")
        start_color_label.setAlignment(Qt.AlignCenter)
        start_color_layout.addWidget(start_color_label)
        
        start_btn = QPushButton()
        start_btn.setFixedSize(60, 30)
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setToolTip("点击选择起始颜色")
        
        # 根据是填充还是线条渐变，设置不同的初始颜色
        if is_fill:
            start_color = self.gradient_start_color
            end_color = self.gradient_end_color
            current_type = self.gradient_type
            current_direction = self.gradient_direction
        else:
            start_color = self.gradient_pen_start_color if hasattr(self, 'gradient_pen_start_color') else QColor(255, 0, 0)
            end_color = self.gradient_pen_end_color if hasattr(self, 'gradient_pen_end_color') else QColor(0, 0, 255)
            current_type = self.gradient_pen_type if hasattr(self, 'gradient_pen_type') else 0
            current_direction = self.gradient_pen_direction if hasattr(self, 'gradient_pen_direction') else 0
            
            # 初始化线条渐变属性（如果尚未初始化）
            if not hasattr(self, 'gradient_pen_start_color'):
                self.gradient_pen_start_color = QColor(255, 0, 0)
                self.gradient_pen_end_color = QColor(0, 0, 255)
                self.gradient_pen_type = 0
                self.gradient_pen_direction = 0
        
        self._update_color_button(start_btn, start_color)
        # 直接连接点击事件到颜色选择
        start_btn.clicked.connect(lambda: self._select_gradient_color(start_btn, preview, True))
        start_color_layout.addWidget(start_btn)
        colors_layout.addLayout(start_color_layout)
        
        # 终点颜色
        end_color_layout = QVBoxLayout()
        end_color_layout.setAlignment(Qt.AlignCenter)
        end_color_layout.setSpacing(8)
        end_label = QLabel("结束颜色")
        end_label.setAlignment(Qt.AlignCenter)
        end_color_layout.addWidget(end_label)
        
        end_btn = QPushButton()
        end_btn.setFixedSize(60, 30)
        end_btn.setCursor(Qt.PointingHandCursor)
        end_btn.setToolTip("点击选择结束颜色")
        self._update_color_button(end_btn, end_color)
        # 直接连接点击事件到颜色选择
        end_btn.clicked.connect(lambda: self._select_gradient_color(end_btn, preview, False))
        end_color_layout.addWidget(end_btn)
        colors_layout.addLayout(end_color_layout)
        
        layout.addLayout(colors_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #c0c0c0;")
        layout.addWidget(separator)
        
        # 渐变类型选择
        type_label = QLabel("渐变类型")
        type_label.setAlignment(Qt.AlignCenter)
        type_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(type_label)
        
        type_group = QButtonGroup(dialog)
        type_layout = QHBoxLayout()
        type_layout.setSpacing(20)
        type_layout.setContentsMargins(20, 0, 20, 0)
        
        linear_radio = QRadioButton("线性渐变")
        linear_radio.setChecked(current_type == 0)
        type_group.addButton(linear_radio, 0)
        type_layout.addWidget(linear_radio)
        
        radial_radio = QRadioButton("径向渐变")
        radial_radio.setChecked(current_type == 1)
        type_group.addButton(radial_radio, 1)
        type_layout.addWidget(radial_radio)
        
        layout.addLayout(type_layout)
        
        # 线性渐变方向选择
        direction_widget = QWidget()
        direction_layout = QVBoxLayout(direction_widget)
        direction_layout.setSpacing(10)
        
        direction_label = QLabel("渐变方向")
        direction_label.setAlignment(Qt.AlignCenter)
        direction_label.setStyleSheet("font-weight: bold;")
        direction_layout.addWidget(direction_label)
        
        direction_group = QButtonGroup(dialog)
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(15)
        dir_layout.setContentsMargins(10, 0, 10, 0)
        
        horizontal_radio = QRadioButton("水平")
        horizontal_radio.setChecked(current_direction == 0)
        direction_group.addButton(horizontal_radio, 0)
        dir_layout.addWidget(horizontal_radio)
        
        vertical_radio = QRadioButton("垂直")
        vertical_radio.setChecked(current_direction == 1)
        direction_group.addButton(vertical_radio, 1)
        dir_layout.addWidget(vertical_radio)
        
        diagonal_radio = QRadioButton("对角线")
        diagonal_radio.setChecked(current_direction == 2)
        direction_group.addButton(diagonal_radio, 2)
        dir_layout.addWidget(diagonal_radio)
        
        direction_layout.addLayout(dir_layout)
        layout.addWidget(direction_widget)
        
        # 显示/隐藏方向选择，基于当前渐变类型
        direction_widget.setVisible(current_type == 0)
        
        # 当渐变类型改变时，显示/隐藏方向选择
        type_group.buttonClicked.connect(lambda btn: direction_widget.setVisible(type_group.id(btn) == 0))
        
        # 更新预览的函数
        def update_preview():
            pixmap = QPixmap(preview.size())
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 获取当前选择的渐变类型和方向
            gradient_type = type_group.checkedId()
            direction = direction_group.checkedId()
            
            # 创建渐变
            if gradient_type == 0:  # 线性渐变
                gradient = QLinearGradient()
                # 设置渐变方向
                if direction == 0:  # 水平
                    gradient.setStart(0, pixmap.height() / 2)
                    gradient.setFinalStop(pixmap.width(), pixmap.height() / 2)
                elif direction == 1:  # 垂直
                    gradient.setStart(pixmap.width() / 2, 0)
                    gradient.setFinalStop(pixmap.width() / 2, pixmap.height())
                else:  # 对角线
                    gradient.setStart(0, 0)
                    gradient.setFinalStop(pixmap.width(), pixmap.height())
            else:  # 径向渐变
                center_x = pixmap.width() / 2
                center_y = pixmap.height() / 2
                radius = min(pixmap.width(), pixmap.height()) / 2
                gradient = QRadialGradient(center_x, center_y, radius)
            
            # 获取当前选择的颜色
            start_color = start_btn.property("color")
            end_color = end_btn.property("color")
            
            # 设置渐变颜色
            gradient.setColorAt(0, start_color)
            gradient.setColorAt(1, end_color)
            
            # 绘制渐变
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(0, 0, pixmap.width(), pixmap.height(), 6, 6)
            
            # 绘制边框
            painter.setPen(QPen(Qt.gray, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(0, 0, pixmap.width() - 1, pixmap.height() - 1, 6, 6)
            
            painter.end()
            
            # 设置预览图像
            preview.setIcon(QIcon(pixmap))
            preview.setIconSize(pixmap.size())
        
        # 设置初始颜色
        start_btn.setProperty("color", start_color)
        end_btn.setProperty("color", end_color)
        
        # 连接信号，更新预览
        type_group.buttonClicked.connect(lambda: update_preview())
        direction_group.buttonClicked.connect(lambda: update_preview())
        
        # 初始化预览
        update_preview()
        
        # 添加确定和取消按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        ok_button = QPushButton("确定")
        ok_button.setMinimumWidth(80)
        ok_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        ok_button.clicked.connect(dialog.accept)
        
        cancel_button = QPushButton("取消")
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(dialog.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # 显示对话框并处理结果
        if dialog.exec_() == QDialog.Accepted:
            # 根据对话框类型处理不同的渐变设置
            if is_fill:
                self.gradient_start_color = start_btn.property("color")
                self.gradient_end_color = end_btn.property("color")
                self.gradient_type = type_group.checkedId()
                self.gradient_direction = direction_group.checkedId()
                
                # 发送渐变色变化信号
                self.gradient_changed.emit(
                    self.gradient_start_color,
                    self.gradient_end_color,
                    self.gradient_type,
                    self.gradient_direction
                )
                
                # 更新预览
                self._update_gradient_preview()
            else:
                self.gradient_pen_start_color = start_btn.property("color")
                self.gradient_pen_end_color = end_btn.property("color")
                self.gradient_pen_type = type_group.checkedId()
                self.gradient_pen_direction = direction_group.checkedId()
                
                # 发送线条渐变色变化信号
                self.gradient_pen_changed.emit(
                    self.gradient_pen_start_color,
                    self.gradient_pen_end_color,
                    self.gradient_pen_type,
                    self.gradient_pen_direction
                )
                
                # 更新预览（如果有线条渐变预览）
                if hasattr(self, '_update_gradient_pen_preview'):
                    self._update_gradient_pen_preview()
    
    def _select_gradient_color(self, button, preview, is_start):
        """选择渐变颜色"""
        current_color = button.property("color") if button.property("color") else QColor(255, 255, 255)
        color = QColorDialog.getColor(current_color, self, "选择颜色", QColorDialog.ShowAlphaChannel)
        
        if color.isValid():
            # 更新按钮颜色
            self._update_color_button(button, color)
            button.setProperty("color", color)
            
            # 更新预览
            if is_start:
                self.gradient_start_color = color
            else:
                self.gradient_end_color = color
                
            # 触发预览更新
            preview.click()

    def _on_gradient_start_clicked(self):
        """渐变起点按钮点击处理"""
        color = QColorDialog.getColor(self.gradient_start_color, self, "选择渐变起始颜色",
                                    QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.gradient_start_color = color
            self._update_color_button(self.gradient_start_btn, color)
            self._update_gradient_preview()

    def _on_gradient_end_clicked(self):
        """渐变终点按钮点击处理"""
        color = QColorDialog.getColor(self.gradient_end_color, self, "选择渐变结束颜色",
                                    QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.gradient_end_color = color
            self._update_color_button(self.gradient_end_btn, color)
            self._update_gradient_preview()

    def _on_gradient_type_changed(self):
        """渐变类型变化处理"""
        self.gradient_type = self.gradient_type_group.checkedId()
        
        # 如果是径向渐变，隐藏方向选择
        if self.gradient_type == 1:  # 径向渐变
            self.direction_widget.hide()
        else:  # 线性渐变
            self.direction_widget.show()
            
        self._update_gradient_preview()

    def _on_gradient_direction_changed(self):
        """渐变方向变化处理"""
        self.gradient_direction = self.direction_group.checkedId()
        self._update_gradient_preview()

    def _on_apply_gradient(self):
        """应用渐变填充处理"""
        # 发送渐变变化信号
        self.gradient_changed.emit(
            self.gradient_start_color,
            self.gradient_end_color,
            self.gradient_type,
            self.gradient_direction
        )

    def _on_disable_gradient(self):
        """取消渐变填充处理"""
        # 发送信号，使用当前填充颜色
        self.color_changed.emit(self.fill_color, True)
        
    def _on_line_width_changed(self, value):
        """线宽变化处理"""
        self.line_width_label.setText(str(value))
        self.line_width_changed.emit(value)
        
    def _on_line_style_changed(self, index):
        """线型变化处理"""
        style = self.line_style_combo.itemData(index)
        self.line_style_changed.emit(style)
        
    def _on_eraser_size_changed(self, value):
        """橡皮擦大小变化处理"""
        self.eraser_size = value
        self.eraser_size_label.setText(str(value))
        self.eraser_size_changed.emit(value)

    def set_current_tool(self, tool_name):
        """设置当前工具"""
        self.current_tool = tool_name
        # 根据工具显示或隐藏相关控件
        self._update_ui_for_tool()
        
    def _update_ui_for_tool(self):
        """根据当前工具更新UI"""
        # 显示或隐藏橡皮擦大小控件
        if self.current_tool == "eraser":
            self.eraser_size_widget.show()
        else:
            self.eraser_size_widget.hide()
        
    def _update_gradient_preview(self):
        """更新渐变预览"""
        pixmap = QPixmap(self.gradient_preview.size())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变
        if self.gradient_type == 0:  # 线性渐变
            gradient = QLinearGradient()
            # 设置渐变方向
            if self.gradient_direction == 0:  # 水平
                gradient.setStart(0, pixmap.height() / 2)
                gradient.setFinalStop(pixmap.width(), pixmap.height() / 2)
            elif self.gradient_direction == 1:  # 垂直
                gradient.setStart(pixmap.width() / 2, 0)
                gradient.setFinalStop(pixmap.width() / 2, pixmap.height())
            else:  # 对角线
                gradient.setStart(0, 0)
                gradient.setFinalStop(pixmap.width(), pixmap.height())
        else:  # 径向渐变
            center_x = pixmap.width() / 2
            center_y = pixmap.height() / 2
            radius = min(pixmap.width(), pixmap.height()) / 2
            gradient = QRadialGradient(center_x, center_y, radius)
        
        # 设置渐变颜色
        gradient.setColorAt(0, self.gradient_start_color)
        gradient.setColorAt(1, self.gradient_end_color)
        
        # 绘制渐变
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, pixmap.width(), pixmap.height())
        
        # 绘制边框
        painter.setPen(QPen(Qt.gray, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
        
        painter.end()
        
        # 设置预览图像
        self.gradient_preview.setIcon(QIcon(pixmap))
        self.gradient_preview.setIconSize(pixmap.size())
        
    def _on_predefined_color_clicked(self, color):
        """处理预定义颜色的点击事件"""
        # 根据当前选择的颜色按钮来决定是设置填充颜色还是线条颜色
        if self.current_color_button == self.pen_color_btn:
            self.pen_color = color
            self._update_color_button(self.pen_color_btn, color)
            self.color_changed.emit(color, False)  # False表示不是填充颜色
        else:
            self.fill_color = color
            self._update_color_button(self.fill_color_btn, color)
            self.color_changed.emit(color, True)  # True表示是填充颜色


class LayerPanel(QWidget):
    """图层面板"""
    
    # 定义信号
    layer_changed = pyqtSignal(str)
    
    def __init__(self, document: DrawingDocument):
        super().__init__()
        
        self.document = document
        
        # 初始化UI
        self.init_ui()
        
        # 连接文档信号
        self.document.layers_changed.connect(self.update_layer_list)
        
        # 禁止初始选择信号
        self.layer_list.blockSignals(True)
        
        # 初始更新图层列表
        self.update_layer_list()
        
        # 恢复信号
        self.layer_list.blockSignals(False)
        
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)  # 减少布局间距
        
        # 添加标题标签
        title_label = QLabel("图层管理")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setMinimumWidth(120)  # 设置最小宽度
        main_layout.addWidget(title_label)
        
        # 创建图层列表
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layer_list.setMinimumWidth(120)  # 设置最小宽度
        self.layer_list.setMinimumHeight(300)  # 设置最小高度，使图层列表更长
        self.layer_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: white;
                padding: 2px;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 25px;
            }
            QListWidget::item:selected {
                background-color: #e0e8f0;
                color: black;
                border: 1px solid #a0a0a0;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #f0f8ff;
            }
        """)
        self.layer_list.itemSelectionChanged.connect(self.on_layer_selected)
        self.layer_list.itemChanged.connect(self.on_layer_item_changed)
        main_layout.addWidget(self.layer_list, 1)  # 设置拉伸因子为1，使列表占据更多空间
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        # 添加图层按钮
        self.add_layer_button = self._create_icon_button("添加新图层", "add")
        self.add_layer_button.clicked.connect(self.on_add_layer)
        button_layout.addWidget(self.add_layer_button)
        
        # 删除图层按钮
        self.remove_layer_button = self._create_icon_button("删除选中图层", "remove")
        self.remove_layer_button.clicked.connect(self.on_remove_layer)
        button_layout.addWidget(self.remove_layer_button)
        
        # 上移图层按钮
        self.move_up_button = self._create_icon_button("上移图层", "up")
        self.move_up_button.clicked.connect(self.on_move_layer_up)
        button_layout.addWidget(self.move_up_button)
        
        # 下移图层按钮
        self.move_down_button = self._create_icon_button("下移图层", "down")
        self.move_down_button.clicked.connect(self.on_move_layer_down)
        button_layout.addWidget(self.move_down_button)
        
        # 重命名图层按钮
        self.rename_layer_button = self._create_icon_button("重命名图层", "rename")
        self.rename_layer_button.clicked.connect(self.on_rename_layer)
        button_layout.addWidget(self.rename_layer_button)
        
        main_layout.addLayout(button_layout)
        
        # 添加底部空间
        main_layout.addStretch(1)
        
    def _create_icon_button(self, tooltip, icon_type):
        """创建带图标的按钮"""
        button = QPushButton()
        button.setToolTip(tooltip)
        button.setFixedSize(32, 32)  # 增加按钮大小
        button.setStyleSheet("""
            QPushButton {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:focus {
                border: 2px solid #a0a0a0;
                outline: none;
            }
        """)
        
        # 创建图标
        pixmap = QPixmap(20, 20)  # 增加图标大小
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据类型绘制不同的图标
        if icon_type == "add":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(10, 5, 10, 15)
            painter.drawLine(5, 10, 15, 10)
        elif icon_type == "remove":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(5, 10, 15, 10)
        elif icon_type == "up":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(10, 5, 10, 15)
            painter.drawLine(5, 10, 10, 5)
            painter.drawLine(10, 5, 15, 10)
        elif icon_type == "down":
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(10, 5, 10, 15)
            painter.drawLine(5, 10, 10, 15)
            painter.drawLine(10, 15, 15, 10)
        elif icon_type == "rename":
            painter.setPen(QPen(Qt.black, 1))
            painter.drawLine(5, 15, 15, 15)
            painter.drawLine(5, 10, 15, 10)
            painter.drawLine(5, 5, 10, 5)
        
        painter.end()
        
        button.setIcon(QIcon(pixmap))
        button.setIconSize(QSize(20, 20))  # 设置图标大小
        return button
        
    def update_layer_list(self):
        """更新图层列表"""
        # 保存当前滚动位置
        scroll_pos = self.layer_list.verticalScrollBar().value()
        
        # 记住当前选中的图层
        current_layer = self.document.current_layer
        
        # 断开信号连接，避免触发不必要的事件
        self.layer_list.blockSignals(True)
        
        # 清空列表
        self.layer_list.clear()
        
        # 反向添加图层（使顶层图层显示在列表顶部）
        selected_item = None
        for layer_name in reversed(self.document.get_layer_names()):
            item = QListWidgetItem()
            
            # 创建自定义小部件来显示图层
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(5)
                
            # 添加可见性复选框
            checkbox = QCheckBox()
            checkbox.setFixedSize(20, 20)
            is_visible = self.document.is_layer_visible(layer_name)
            checkbox.setChecked(is_visible)
            checkbox.setToolTip("显示/隐藏图层")
            
            # 使用lambda捕获当前图层名称
            checkbox.stateChanged.connect(
                lambda state, name=layer_name: 
                self.document.set_layer_visibility(name, state == Qt.Checked)
            )
            
            layout.addWidget(checkbox)
            
            # 添加图层名称标签
            label = QLabel(layer_name)
            if layer_name == current_layer:
                label.setStyleSheet("font-weight: bold; color: #3366CC;")
            layout.addWidget(label, 1)  # 设置stretch为1，使标签占用剩余空间
            
            # 设置项目
            self.layer_list.addItem(item)
            item.setData(Qt.UserRole, layer_name)  # 存储图层名称
            item.setSizeHint(widget.sizeHint())
            self.layer_list.setItemWidget(item, widget)
            
            # 保存选中图层的项目引用
            if layer_name == current_layer:
                selected_item = item
        
        # 恢复滚动位置
        self.layer_list.verticalScrollBar().setValue(scroll_pos)
        
        # 设置选中项
        if selected_item:
            selected_item.setSelected(True)
            self.layer_list.setCurrentItem(selected_item)
        
        # 更新按钮状态
        self._update_button_states()
        
        # 恢复信号处理
        self.layer_list.blockSignals(False)
        
    def _update_button_states(self):
        """更新按钮状态"""
        current_row = self.layer_list.currentRow()
        count = self.layer_list.count()
        
        # 设置上移按钮状态
        self.move_up_button.setEnabled(current_row > 0)
        
        # 设置下移按钮状态
        self.move_down_button.setEnabled(current_row >= 0 and current_row < count - 1)
        
        # 设置删除按钮状态（至少保留一个图层）
        self.remove_layer_button.setEnabled(count > 1 and current_row >= 0)
        
        # 设置重命名按钮状态
        self.rename_layer_button.setEnabled(current_row >= 0)
        
    def on_layer_selected(self):
        """图层选择处理"""
        # 阻止递归信号
        if self.layer_list.signalsBlocked():
            return
            
        selected_items = self.layer_list.selectedItems()
        if selected_items:
            layer_name = selected_items[0].data(Qt.UserRole)
            if layer_name and layer_name != self.document.current_layer:
                self.document.set_current_layer(layer_name)
                
                # 更新图层列表以刷新高亮显示
                self.update_layer_list()
                
                # 发送图层变更信号
                self.layer_changed.emit(layer_name)
                
                # 更新按钮状态
                self._update_button_states()
            
    def on_layer_item_changed(self, item):
        """图层项变化处理（复选框状态改变）"""
        layer_name = item.data(Qt.UserRole)
        is_visible = item.checkState() == Qt.Checked
        self.document.set_layer_visibility(layer_name, is_visible)
        
    def on_add_layer(self):
        """添加图层处理"""
        # 获取一个唯一的图层名称
        base_name = "新图层"
        counter = 1
        layer_name = base_name
        
        while layer_name in self.document.get_layer_names():
            layer_name = f"{base_name} {counter}"
            counter += 1
            
        # 添加新图层
        self.document.add_layer(layer_name)
        
        # 更新图层列表
        self.update_layer_list()
        
        # 选择新图层
        for i in range(self.layer_list.count()):
            if self.layer_list.item(i).text() == layer_name:
                self.layer_list.setCurrentRow(i)
                break
                
    def on_remove_layer(self):
        """删除图层处理"""
        selected_items = self.layer_list.selectedItems()
        if selected_items and self.layer_list.count() > 1:
            layer_name = selected_items[0].data(Qt.UserRole)
            
            # 确认删除
            reply = QMessageBox.question(self, "确认删除", 
                                        f"确定要删除图层 '{layer_name}' 吗？\n该操作将删除图层中的所有图形。",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.document.remove_layer(layer_name)
                if success:
                    # 强制更新图层列表
                    self.update_layer_list()
                    self.set_status_message(f"已删除图层: {layer_name}")
                else:
                    QMessageBox.warning(self, "删除失败", "无法删除最后一个图层。")
                    
    def on_move_layer_up(self):
        """上移图层处理 - 在列表中向上移动，在文档中是向下移动"""
        current_row = self.layer_list.currentRow()
        if current_row > 0:
            # 获取当前图层名称
            current_layer_name = self.layer_list.item(current_row).data(Qt.UserRole)
            if current_layer_name:
                # 移动图层
                self.document.move_layer_down(current_layer_name)
                
                # 断开信号连接，避免触发不必要的事件
                self.layer_list.blockSignals(True)
                
                # 保存当前滚动位置
                scroll_pos = self.layer_list.verticalScrollBar().value()
                
                # 清空列表
                self.layer_list.clear()
                
                # 反向添加图层（使顶层图层显示在列表顶部）
                selected_item = None
                for layer_name in reversed(self.document.get_layer_names()):
                    item = QListWidgetItem()
                    
                    # 创建自定义小部件来显示图层
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    layout.setContentsMargins(2, 2, 2, 2)
                    layout.setSpacing(5)
                    
                    # 添加可见性复选框
                    checkbox = QCheckBox()
                    checkbox.setFixedSize(20, 20)
                    is_visible = self.document.is_layer_visible(layer_name)
                    checkbox.setChecked(is_visible)
                    checkbox.setToolTip("显示/隐藏图层")
                    
                    # 使用lambda捕获当前图层名称
                    checkbox.stateChanged.connect(
                        lambda state, name=layer_name: 
                        self.document.set_layer_visibility(name, state == Qt.Checked)
                    )
                    
                    layout.addWidget(checkbox)
                    
                    # 添加图层名称标签
                    label = QLabel(layer_name)
                    if layer_name == current_layer_name:
                        label.setStyleSheet("font-weight: bold; color: #3366CC;")
                    layout.addWidget(label, 1)  # 设置stretch为1，使标签占用剩余空间
                    
                    # 设置项目
                    self.layer_list.addItem(item)
                    item.setData(Qt.UserRole, layer_name)  # 存储图层名称
                    item.setSizeHint(widget.sizeHint())
                    self.layer_list.setItemWidget(item, widget)
                    
                    # 保存选中图层的项目引用
                    if layer_name == current_layer_name:
                        selected_item = item
                
                # 恢复滚动位置
                self.layer_list.verticalScrollBar().setValue(scroll_pos)
                
                # 设置选中项
                if selected_item:
                    selected_item.setSelected(True)
                    self.layer_list.setCurrentItem(selected_item)
                
                # 更新按钮状态
                self._update_button_states()
                
                # 恢复信号处理
                self.layer_list.blockSignals(False)
                
                # 保持焦点在按钮上以便连续操作
                self.move_up_button.setFocus()
    
    def on_move_layer_down(self):
        """下移图层处理 - 在列表中向下移动，在文档中是向上移动"""
        current_row = self.layer_list.currentRow()
        if current_row >= 0 and current_row < self.layer_list.count() - 1:
            # 获取当前图层名称
            current_layer_name = self.layer_list.item(current_row).data(Qt.UserRole)
            if current_layer_name:
                # 移动图层
                self.document.move_layer_up(current_layer_name)
                
                # 断开信号连接，避免触发不必要的事件
                self.layer_list.blockSignals(True)
                
                # 保存当前滚动位置
                scroll_pos = self.layer_list.verticalScrollBar().value()
                
                # 清空列表
                self.layer_list.clear()
                
                # 反向添加图层（使顶层图层显示在列表顶部）
                selected_item = None
                for layer_name in reversed(self.document.get_layer_names()):
                    item = QListWidgetItem()
                    
                    # 创建自定义小部件来显示图层
                    widget = QWidget()
                    layout = QHBoxLayout(widget)
                    layout.setContentsMargins(2, 2, 2, 2)
                    layout.setSpacing(5)
                    
                    # 添加可见性复选框
                    checkbox = QCheckBox()
                    checkbox.setFixedSize(20, 20)
                    is_visible = self.document.is_layer_visible(layer_name)
                    checkbox.setChecked(is_visible)
                    checkbox.setToolTip("显示/隐藏图层")
                    
                    # 使用lambda捕获当前图层名称
                    checkbox.stateChanged.connect(
                        lambda state, name=layer_name: 
                        self.document.set_layer_visibility(name, state == Qt.Checked)
                    )
                    
                    layout.addWidget(checkbox)
                    
                    # 添加图层名称标签
                    label = QLabel(layer_name)
                    if layer_name == current_layer_name:
                        label.setStyleSheet("font-weight: bold; color: #3366CC;")
                    layout.addWidget(label, 1)  # 设置stretch为1，使标签占用剩余空间
                    
                    # 设置项目
                    self.layer_list.addItem(item)
                    item.setData(Qt.UserRole, layer_name)  # 存储图层名称
                    item.setSizeHint(widget.sizeHint())
                    self.layer_list.setItemWidget(item, widget)
                    
                    # 保存选中图层的项目引用
                    if layer_name == current_layer_name:
                        selected_item = item
                
                # 恢复滚动位置
                self.layer_list.verticalScrollBar().setValue(scroll_pos)
                
                # 设置选中项
                if selected_item:
                    selected_item.setSelected(True)
                    self.layer_list.setCurrentItem(selected_item)
                
                # 更新按钮状态
                self._update_button_states()
                
                # 恢复信号处理
                self.layer_list.blockSignals(False)
                
                # 保持焦点在按钮上以便连续操作
                self.move_down_button.setFocus()
    
    def on_rename_layer(self):
        """重命名图层处理"""
        current_row = self.layer_list.currentRow()
        if current_row >= 0:
            old_name = self.layer_list.item(current_row).data(Qt.UserRole)
            
            # 弹出重命名对话框
            new_name, ok = QInputDialog.getText(self, "重命名图层", 
                                             "输入新的图层名称:", 
                                             QLineEdit.Normal, old_name)
            
            if ok and new_name and new_name != old_name:
                # 检查名称是否已存在
                if new_name in self.document.get_layer_names():
                    QMessageBox.warning(self, "重命名失败", 
                                      f"图层名称 '{new_name}' 已存在。\n请使用其他名称。")
                else:
                    self.document.rename_layer(old_name, new_name)
                    self.update_layer_list()
                    
                    # 保持选择
                    for i in range(self.layer_list.count()):
                        if self.layer_list.item(i).data(Qt.UserRole) == new_name:
                            self.layer_list.setCurrentRow(i)
                            break
                            
    def set_status_message(self, message):
        """设置状态栏消息"""
        # 查找主窗口
        parent = self.parent()
        while parent and not hasattr(parent, 'set_status_message'):
            parent = parent.parent()
            
        if parent and hasattr(parent, 'set_status_message'):
            parent.set_status_message(message)