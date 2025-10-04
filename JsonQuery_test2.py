# @time: 2025-10-03 16:30:35
# @author:HQ
import tkinter as tk
import tkinter.font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re
import json
from ttkbootstrap.dialogs import Messagebox

# 定义 JsonQueryClient 类，现在继承自 ttk.Frame
class JsonQueryClient(ttk.Frame):
    # 增加 editor_width 和 editor_height 参数，并设置默认值
    def __init__(self, parent, window_id_num, editor_width=40, editor_height=20):
        super().__init__(parent, padding=10, relief="groove", borderwidth=2)
        self.window_id = window_id_num
        self.editor_font = tkfont.Font(family="Courier", size=10)

        # 保存传入的尺寸
        self.editor_width = editor_width
        self.editor_height = editor_height

        self.create_widgets()

        self.after_idle(self._update_line_numbers)

    def create_widgets(self):
        """创建 JsonQueryClient 内部的所有组件"""
        self.create_param_bar()  # 创建参数栏
        self.create_json_editor()  # 创建 JSON 编辑器

        # 初始化更新行号 (可能需要延迟调用，确保组件已渲染)
        # 延迟调用，确保winfo_height等可用，并且在首次渲染后立即更新
        self.after_idle(self._update_line_numbers)  # 使用 after_idle 更好

    def create_param_bar(self):
        # ... 保持不变 ...
        param_frame = ttk.Frame(self)
        param_frame.pack(side=TOP, fill=X, pady=(0, 5))

        self.check_var = ttk.IntVar(value=0)
        self.check_button = ttk.Checkbutton(param_frame, style=SUCCESS, variable=self.check_var,
                                            text=f"Window {self.window_id}")
        self.check_button.pack(side=LEFT, padx=5)

        ttk.Label(param_frame, text="备注:").pack(side=LEFT, padx=(5, 0))
        self.date_entry = ttk.Entry(param_frame, width=15)
        self.date_entry.pack(side=LEFT, padx=(0, 5))

        self.query_button = ttk.Button(param_frame, text="查询", style=SUCCESS, command=self._local_json_query)
        self.query_button.pack(side=LEFT, padx=(5, 0))

        self.query_entry = ttk.Entry(param_frame, width=15)
        self.query_entry.pack(side=LEFT, padx=(0, 5))

        self.window_info = ttk.Button(param_frame, text="窗口信息", style=WARNING, command=self.perform_query_info)
        self.window_info.pack(side=LEFT, padx=5)

        self.json_serializable_button=ttk.Button(param_frame,text="JSON 序列化",style=PRIMARY,command=self.json_serializable)
        self.json_serializable_button.pack(side=LEFT,padx=5)

    def create_json_editor(self):
        """使用 pack 嵌套布局实现 JSON 编辑器"""
        editor_frame = ttk.Frame(self)
        editor_frame.pack(side=TOP, fill=BOTH, expand=True)

        container = ttk.Frame(editor_frame)
        container.pack(fill=BOTH, expand=True)

        self.line_number_text = tk.Text(container,
                                        width=4,
                                        padx=4,
                                        pady=4,
                                        state="disabled",
                                        font=self.editor_font,
                                        background="#2d2d2d",
                                        foreground="#aaaaaa",
                                        relief="flat")
        self.line_number_text.pack(side=LEFT, fill=Y)

        editor_area = ttk.Frame(container)
        editor_area.pack(side=LEFT, fill=BOTH, expand=True)

        self.content_text = tk.Text(editor_area,
                                    wrap="none",
                                    font=self.editor_font,
                                    undo=True,
                                    relief="flat",
                                    width=self.editor_width,   # 使用实例变量
                                    height=self.editor_height) # 使用实例变量
        self.content_text.pack(side=TOP, fill=BOTH, expand=True)

        hscroll = ttk.Scrollbar(editor_area, orient=HORIZONTAL, command=self.content_text.xview,style="light-round")
        hscroll.pack(side=BOTTOM, fill=X)
        self.content_text.config(xscrollcommand=hscroll.set)

        vscroll = ttk.Scrollbar(container, orient=VERTICAL, command=self._sync_yviews,style="light-round")
        vscroll.pack(side=RIGHT, fill=Y)
        self.content_text.config(yscrollcommand=vscroll.set)
        self.line_number_text.config(yscrollcommand=vscroll.set)

        self.content_text.bind("<Double-1>", self.on_double_click)
        self.content_text.bind("<KeyRelease>", self._update_line_numbers)
        self.content_text.bind("<MouseWheel>", self._update_line_numbers)
        self.content_text.bind("<Button-4>", self._update_line_numbers)
        self.content_text.bind("<Button-5>", self._update_line_numbers)
        self.content_text.bind("<Configure>", self._update_line_numbers)

    # ... (JsonQueryClient 的其他方法保持不变) ...
    def _sync_yviews(self, *args):
        self.content_text.yview(*args)
        self.line_number_text.yview(*args)
        self._update_line_numbers()

    def _update_line_numbers(self, event=None):  # event=None 确保在没有事件时也能调用
        """更新行号显示"""
        if not self.winfo_exists():  # 如果组件已销毁，则不执行
            return

        self.line_number_text.config(state="normal")
        self.line_number_text.delete("1.0", tk.END)

        total_lines = int(self.content_text.index('end-1c').split('.')[0])
        first_visible_line_idx = self.content_text.index("@0,0")
        last_visible_line_idx = self.content_text.index(f"@0,{self.content_text.winfo_height()}")

        first_line = int(first_visible_line_idx.split('.')[0])
        last_line = int(last_visible_line_idx.split('.')[0])

        if last_visible_line_idx != f"{last_line}.0":
            last_line += 1
        last_line = min(total_lines, last_line)

        first_line = max(1, first_line)

        if self.content_text.bbox(f"{last_line}.0") is not None:
            if self.content_text.bbox(f"{last_line}.0")[1] < self.content_text.winfo_height():
                if last_line < total_lines:
                    last_line += 1

        lines = "\n".join(str(i) for i in range(first_line, last_line + 1))

        if self.editor_font and self.content_text.winfo_exists():
            line_height = self.editor_font.metrics("linespace")
            if self.content_text.winfo_height() > 0 and line_height > 0:
                content_height_in_lines = self.content_text.winfo_height() // line_height
            else:
                content_height_in_lines = 0

            current_lines_shown = len(range(first_line, last_line + 1))
            if current_lines_shown < content_height_in_lines:
                lines += "\n" * (content_height_in_lines - current_lines_shown)

        self.line_number_text.insert("1.0", lines)
        self.line_number_text.config(state="disabled")

    def perform_query_info(self, event=None):
        """执行窗口信息查询操作"""
        check_val = self.check_var.get()
        json_input_snippet = self.content_text.get("1.0", "1.end").strip()  # 只取第一行
        date = self.date_entry.get()
        query_text = self.query_entry.get().strip() # 从自己的输入框获取查询内容

        print(
            f"Window {self.window_id} Info: Checkbox={check_val}, Remark='{date}', query_text='{query_text}', First line of JSON='{json_input_snippet}'")

    def on_double_click(self, event):
        self.content_text.event_generate("<<Clear>>")
        self.content_text.tag_remove("sel", "1.0", "end")

        index = self.content_text.index(f"@{event.x},{event.y}")
        line_start = f"{index.split('.')[0]}.0"
        line_end = f"{index.split('.')[0]}.end"
        line_content = self.content_text.get(line_start, line_end)

        col_num = int(index.split('.')[1])

        word_pattern = r"\w+"

        for match in re.finditer(word_pattern, line_content, re.UNICODE):
            start_col, end_col = match.span()

            if start_col <= col_num < end_col:
                word_start_index = f"{index.split('.')[0]}.{start_col}"
                word_end_index = f"{index.split('.')[0]}.{end_col}"

                self.content_text.tag_add("sel", word_start_index, word_end_index)
                self.content_text.mark_set("insert", word_end_index)
                self.content_text.see(word_start_index)

                return "break"

        return

    def _local_json_query(self, query_text=None):  # 可以接受外部查询，也可以使用内部查询
        """执行查询操作，匹配并高亮显示"""
        self.content_text.tag_remove("highlight", "1.0", "end")  # 清除现有高亮

        if query_text is None:  # 如果没有外部查询，使用内部输入框内容
            query = self.query_entry.get().strip()
        else:
            query = query_text.strip()

        if not query:
            return

        self.content_text.tag_configure("highlight", background="yellow", foreground="black")

        start = "1.0"
        while True:
            pos = self.content_text.search(query, start, stopindex="end")
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            self.content_text.tag_add("highlight", pos, end_pos)
            start = end_pos

    def json_serializable(self):
        try:
            text_content=self.content_text.get(1.0,END).strip()
            print("输入内容:", text_content)
            print("输入类型:", type(text_content))

            # 尝试解析为 Python 对象
            python_data = json.loads(text_content)  # 解析 JSON 字符串为 Python 对象

            # 序列化为格式化的 JSON 字符串
            json_string = json.dumps(python_data, indent=4, ensure_ascii=False)

            # 清空 tk.Text 并插入格式化后的 JSON
            self.content_text.delete(1.0, END)
            self.content_text.insert(END, json_string)

            self.after_idle(self._update_line_numbers)
            return {"status": "success", "data": json_string,'window_id':self.window_id}
        except Exception as e:
            print(f'JSON 序列化失败，填写数据格式异常。\n报错信息如下：{e}')
            # Messagebox.show_error(title='JSON 序列化',message=f"'Window{self.window_id}' JSON 序列化失败，填写数据格式异常。\n报错信息如下：{e}")
            return {"status": "error", 'window_id':self.window_id,"message": f"Window {self.window_id}: 序列化失败: {e}"}

# 简单的测试运行 (可选，主要用于开发时测试 JsonQueryClient 自身)
if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    app.title("JsonQueryClient Standalone Test")

    # 示例JsonQueryClient，可以传入自定义尺寸
    client1 = JsonQueryClient(app, 1, editor_width=30, editor_height=35)
    client1.pack(fill=BOTH, expand=True, padx=10, pady=10)

    app.mainloop()