#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_tools_file():
    """修复tools.py文件中的缩进错误"""
    file_path = 'DrawPicture/models/tools.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复SelectionTool类中的缩进错误
    content = content.replace(
        """            if move_distance > self.click_threshold or self.moving:
                self.moving = True
                delta = QPointF(current_pos - self.last_position)
            self.document.move_selected_shapes(delta)
                self.last_position = current_pos""",
        
        """            if move_distance > self.click_threshold or self.moving:
                self.moving = True
                delta = QPointF(current_pos - self.last_position)
                self.document.move_selected_shapes(delta)
                self.last_position = current_pos"""
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("tools.py文件缩进错误修复完成！")

if __name__ == "__main__":
    fix_tools_file() 