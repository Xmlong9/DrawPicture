#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_document_file():
    """修复document.py文件中的所有缩进错误"""
    file_path = 'DrawPicture/models/document.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复remove_shape方法中的缩进错误
    content = content.replace(
        """        if shape in self.shapes:
            # 记录操作用于撤销
        self.record_state()""",
        
        """        if shape in self.shapes:
            # 记录操作用于撤销
            self.record_state()"""
    )
    
    # 修复clear方法中的缩进错误
    content = content.replace(
        """        if self.shapes:
        self.record_state()""",
        
        """        if self.shapes:
            self.record_state()"""
    )
    
    # 修复delete_selected_shapes方法中的缩进错误
    content = content.replace(
        """        if not self.selected_shapes:
            return
            
        self.record_state()""",
        
        """        if not self.selected_shapes:
            return
            
            self.record_state()"""
    )
    
    # 修复delete_selected_shapes方法中的shapes.remove缩进错误
    content = content.replace(
        """            if shape in self.shapes:
            self.shapes.remove(shape)""",
        
        """            if shape in self.shapes:
                self.shapes.remove(shape)"""
    )
    
    # 修复remove_layer方法中的缩进错误
    content = content.replace(
        """        # 记录状态用于撤销/重做
        self.record_state()""",
        
        """        # 记录状态用于撤销/重做
            self.record_state()"""
    )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("所有缩进错误修复完成！")

if __name__ == "__main__":
    fix_document_file() 