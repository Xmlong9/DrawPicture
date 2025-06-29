#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_canvas_file():
    """修复canvas.py文件中的缩进错误"""
    file_path = 'DrawPicture/views/canvas.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修复缩进错误
    fixed_lines = []
    for i, line in enumerate(lines):
        # 修复toggle_grid方法中的缩进错误
        if i > 0 and "def toggle_grid" in lines[i-1] and "self.grid_visible = not self.grid_visible" in line and line.startswith("            "):
            fixed_lines.append("        " + line.lstrip())
        # 修复zoom_in和zoom_out方法中的缩进错误
        elif "self.status_message.emit" in line and "缩放:" in line and line.startswith("            "):
            fixed_lines.append("        " + line.lstrip())
        else:
            fixed_lines.append(line)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("canvas.py文件缩进错误修复完成！")

if __name__ == "__main__":
    fix_canvas_file() 