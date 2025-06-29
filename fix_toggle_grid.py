#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_toggle_grid():
    """修复canvas.py文件中toggle_grid方法的缩进错误"""
    file_path = 'DrawPicture/views/canvas.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到toggle_grid方法并修复缩进
    for i in range(len(lines)):
        if "def toggle_grid" in lines[i]:
            # 找到方法定义后的第二行（应该是self.grid_visible = not self.grid_visible）
            if i+2 < len(lines) and "self.grid_visible = not self.grid_visible" in lines[i+2]:
                # 修复缩进
                lines[i+2] = "        self.grid_visible = not self.grid_visible\n"
                break
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("toggle_grid方法缩进错误修复完成！")

if __name__ == "__main__":
    fix_toggle_grid() 