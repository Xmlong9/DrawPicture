#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_document_file():
    """修复document.py文件中的缩进错误"""
    file_path = 'DrawPicture/models/document.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修复缩进错误
    fixed_lines = []
    for i, line in enumerate(lines):
        if i > 0 and "if shape in self.shapes:" in lines[i-1] and "self.shapes.remove(shape)" in line and not line.startswith("                "):
            # 修复图形删除的缩进
            fixed_lines.append("                " + line.lstrip())
        elif i > 0 and "if len(self.layers) <= 1:" in lines[i-2] and "return False" in lines[i-1] and "self.record_state()" in line and not line.startswith("        "):
            # 修复remove_layer方法中的record_state缩进
            fixed_lines.append("        " + line.lstrip())
        elif i > 0 and "if not self.selected_shapes:" in lines[i-2] and "return" in lines[i-1] and "self.record_state()" in line and not line.startswith("        "):
            # 修复delete_selected_shapes方法中的record_state缩进
            fixed_lines.append("        " + line.lstrip())
        else:
            fixed_lines.append(line)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("文件修复完成！")

if __name__ == "__main__":
    fix_document_file() 