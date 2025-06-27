# 绘图与图形管理

一个基于Python和PyQt5开发的功能丰富的绘图应用程序，支持多种图形绘制、编辑和管理功能。

## 功能特点

- **基本图形绘制**：直线、矩形、圆形
- **特殊曲线绘制**：阿基米德螺线、正弦曲线
- **自由绘制**：可以自由手绘线条
- **图形编辑**：选择、移动、旋转、缩放、复制、删除
- **样式设置**：线条颜色、线宽、线型、填充颜色
- **多图层支持**：添加、重命名、显示/隐藏、删除图层
- **文件操作**：保存、打开、导出图片
- **其他功能**：撤销/重做、网格显示、缩放画布

## 运行环境要求

- Python 3.6+
- PyQt5
- NumPy
- Matplotlib
- Pillow

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 使用说明

### 基本操作

1. **选择工具**：
   - 通过工具面板或菜单栏选择绘图工具
   - 支持选择、直线、矩形、圆形、自由绘制、螺线、正弦曲线等工具

2. **绘制图形**：
   - 在画布上按住鼠标左键并拖动来绘制图形
   - 根据不同工具，图形的绘制方式会有所不同

3. **选择和编辑图形**：
   - 使用选择工具点击图形进行选择
   - 选中图形后可以移动、旋转或缩放
   - 可以按Delete键删除选中的图形
   - 可以按Ctrl+C复制选中的图形

4. **设置样式**：
   - 通过颜色面板设置线条颜色、填充颜色、线宽和线型
   - 样式设置会应用到当前选中的图形或之后创建的新图形

5. **图层管理**：
   - 通过图层面板添加新图层
   - 可以切换活动图层、显示/隐藏图层
   - 可以重命名或删除图层

6. **文件操作**：
   - 通过菜单栏的文件菜单进行新建、打开、保存操作
   - 支持导出为PNG、JPG等图片格式

7. **视图操作**：
   - 使用Ctrl+滚轮缩放画布
   - 通过视图菜单切换网格显示

### 快捷键

- Ctrl+N：新建文档
- Ctrl+O：打开文档
- Ctrl+S：保存文档
- Ctrl+Shift+S：另存为
- Ctrl+Z：撤销
- Ctrl+Y：重做
- Delete：删除选中的图形
- Ctrl+C：复制选中的图形
- Ctrl+加号：放大
- Ctrl+减号：缩小

## 项目结构

- `models/`: 数据模型
  - `shapes.py`: 定义图形类
  - `document.py`: 文档管理类
  - `tools.py`: 工具定义类
- `views/`: 视图层
  - `main_window.py`: 主窗口
  - `canvas.py`: 绘图画布
  - `panels.py`: 工具面板、颜色面板、图层面板
- `controllers/`: 控制器层
  - `tool_controller.py`: 工具控制器
  - `document_controller.py`: 文档控制器
- `resources/`: 资源文件
  - `icons/`: 图标资源
- `main.py`: 程序入口

## 代码示例

### 创建自定义图形

可以通过继承`Shape`类来创建自定义图形：

```python
from models.shapes import Shape
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainterPath

class Star(Shape):
    """五角星图形"""
    def __init__(self, center_x=0, center_y=0, outer_radius=50, inner_radius=25):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        
    def _draw(self, painter):
        path = self._create_star_path()
        painter.drawPath(path)
        
    def _create_star_path(self):
        """创建五角星路径"""
        path = QPainterPath()
        
        # 计算五角星的顶点
        points = []
        for i in range(10):
            angle = i * 36 * math.pi / 180  # 每36度一个点
            radius = self.outer_radius if i % 2 == 0 else self.inner_radius
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)
            points.append((x, y))
            
        # 绘制路径
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)
        path.closeSubpath()
        
        return path
        
    def contains(self, point):
        # 检查点是否在五角星内
        path = self._create_star_path()
        return path.contains(point)
        
    def bounding_rect(self):
        # 返回边界矩形
        return QRectF(
            self.center_x - self.outer_radius,
            self.center_y - self.outer_radius,
            self.outer_radius * 2,
            self.outer_radius * 2
        )
```

## 扩展功能

该项目可以进一步扩展，添加更多功能：

1. 更多绘图工具：多边形、曲线、文本等
2. 更丰富的图形变换：倾斜、反射等
3. 图形对齐功能
4. 图形组合与分解
5. 图层特效：透明度、混合模式等
6. 矢量/位图混合支持
7. 支持SVG导入/导出
8. 更多图形属性编辑选项

## 联系方式

如有问题或建议，请提交Issue或联系开发者。 