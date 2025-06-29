#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fix_document_file():
    """修复document.py文件中的缩进错误"""
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
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("文件修复完成！")

if __name__ == "__main__":
    fix_document_file() 