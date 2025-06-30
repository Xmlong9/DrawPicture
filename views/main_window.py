    def on_eraser_size_changed(self, size):
        """橡皮擦大小变化处理"""
        if "eraser" in self.tools:
            self.tools["eraser"].set_eraser_size(size)
            self.set_status_message(f"橡皮擦大小: {size}")
    
    def on_gradient_changed(self, start_color, end_color, gradient_type, direction):
        """渐变色变化处理"""
        # 设置渐变填充
        self.color_tool.set_gradient_fill(start_color, end_color, gradient_type, direction)
        
        # 应用到选中的图形
        if self.document.selected_shapes:
            self.document.record_state()  # 记录状态用于撤销
            for shape in self.document.selected_shapes:
                shape.set_brush(self.color_tool.get_brush())
            self.document.document_changed.emit()  # 更新显示
            
        # 设置状态消息
        gradient_type_str = "线性" if gradient_type == 0 else "径向"
        direction_str = ""
        if gradient_type == 0:  # 线性渐变
            if direction == 0:
                direction_str = "水平"
            elif direction == 1:
                direction_str = "垂直"
            else:
                direction_str = "对角线"
        
        self.set_status_message(f"已应用{gradient_type_str}渐变填充{direction_str}")
        
    def on_shape_selected(self, shape_type, params): 