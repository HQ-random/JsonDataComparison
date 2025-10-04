# @time: 2025-10-03 16:37:19
# @author:HQ
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from JsonGadget.JsonQuery_test2 import JsonQueryClient


class Comparison(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("JSON 数据对比")
        self.geometry("1600x800")

        self.next_window_id = 1
        self.json_clients = []

        self.create_top_bar()
        self.create_scrollable_area()

        self.add_json_client()
        self.add_json_client()

    def create_top_bar(self):
        # ... 保持不变 ...
        top_bar_frame = ttk.Frame(self, padding=10)
        top_bar_frame.pack(side=TOP, fill=X)

        # 创建内部框架用于居中组件
        inner_frame=ttk.Frame(top_bar_frame)
        inner_frame.pack(expand=True)

        self.query_button = ttk.Button(inner_frame, text="全局查询", style=SUCCESS, command=self.perform_global_query)
        self.query_button.pack(side=LEFT)
        self.global_query_entry = ttk.Entry(inner_frame, width=20)
        self.global_query_entry.pack(side=LEFT, padx=(0, 5))

        self.global_json_serializable_button=ttk.Button(inner_frame,text='JSON 序列化',style=SUCCESS,command=self.perform_global_json)
        self.global_json_serializable_button.pack(side=LEFT,padx=5)

        self.add_button = ttk.Button(inner_frame, text="新增", style=PRIMARY, command=self.add_json_client)
        self.add_button.pack(side=LEFT, padx=5)

        self.delete_button = ttk.Button(inner_frame, text="删除", style=DANGER, command=self.delete_selected_clients)
        self.delete_button.pack(side=LEFT, padx=5)

    def create_scrollable_area(self):
        self.canvas = tk.Canvas(self, bg=self.style.lookup("TFrame", "background"), highlightthickness=0) # highlightthickness=0 可以消除Canvas自己的边框
        self.canvas.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)

        self.clients_container = ttk.Frame(self.canvas, padding=0)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.clients_container, anchor="nw")

        self.h_scrollbar = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview,style="light-round")
        self.h_scrollbar.pack(side=BOTTOM, fill=X)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set)

        self.clients_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.after_idle(self._on_frame_configure)

    def _on_frame_configure(self, event=None):
        """当内部容器 Frame 大小改变时，更新 Canvas 的滚动区域和内部 window 的宽度"""
        self.canvas.update_idletasks() # 强制更新布局，确保winfo_reqwidth是准确的

        # 获取 clients_container 的实际内容宽度和高度
        # 这里使用 winfo_reqwidth/height 更准确地反映了所有子部件所需的总尺寸
        content_width = self.clients_container.winfo_reqwidth()
        content_height = self.clients_container.winfo_reqheight()

        # 获取 Canvas 当前可见区域的宽度和高度
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 确保 canvas_window 的宽度能够容纳所有子部件，并且不小于 canvas 自身的宽度
        # 这样即使内容不足以填满 canvas，window 也至少有 canvas 那么宽，避免了压缩
        window_width = max(content_width, canvas_width)
        window_height = max(content_height, canvas_height)

        # 更新 canvas_window 的尺寸，这很重要，它决定了实际可见的区域
        # 明确设置 height=window_height 确保当内容较少时，container的高度也至少与canvas一样高
        self.canvas.itemconfig(self.canvas_window, width=window_width, height=window_height)

        # 更新 Canvas 的滚动区域，使其包含所有内容
        self.canvas.config(scrollregion=(0, 0, window_width, window_height))

        # 调试信息 (可以在开发时取消注释)
        # print(f"Frame Configure: Container req_width={content_width}, req_height={content_height}")
        # print(f"Canvas size: width={canvas_width}, height={canvas_height}")
        # print(f"Canvas Window set to: width={window_width}, height={window_height}")
        # print(f"Scrollregion set to: {self.canvas.cget('scrollregion')}")


    def _on_canvas_configure(self, event=None):
        """当 Canvas 自身大小改变时，调整 canvas_window 的宽度和高度"""
        # 简单地调用 _on_frame_configure 即可，因为它已经包含了对 window 尺寸的调整逻辑
        self._on_frame_configure()


    def add_json_client(self):
        """新增一个 JsonQueryClient 实例并添加到容器中"""
        # 可以在这里指定每个客户端的编辑器宽度和高度
        # 例如，现在设置为宽度70个字符，高度25行
        new_client = JsonQueryClient(self.clients_container, self.next_window_id,
                                     editor_width=20,  # 自定义宽度
                                     editor_height=25) # 自定义高度
        # fill=Y 确保垂直方向填充，padx/pady 添加间距，expand=False 避免它自行水平扩展
        new_client.pack(side=LEFT, fill=Y, padx=5, pady=5, expand=False)

        self.json_clients.append(new_client)
        self.next_window_id += 1

        self.after_idle(self._on_frame_configure) # 确保 pack 布局完成后再更新

    def delete_selected_clients(self):
        # ... 保持不变 ...
        clients_to_keep = []
        if len(self.json_clients)==0:
            Messagebox.show_error(title='删除',message='客户端为空，不可删除。')
        else:
            for client in self.json_clients:
                if client.check_var.get() == 1:
                    client.destroy()
                else:
                    clients_to_keep.append(client)

            self.json_clients = clients_to_keep

            if not self.json_clients:
                print("所有客户端已删除，自动添加一个新客户端。")
                okcancel_msg=Messagebox.okcancel(title='删除',message='所有客户端已删除，是否自动添加一个新客户端？',
                                                 buttons=['取消:DANGER','确认:SUCCESS'])
                if okcancel_msg=='确认':
                    self.add_json_client() # 自动添加一个新客户端

            self.after_idle(self._on_frame_configure)

    def perform_global_query(self):
        # ... 保持不变 ...
        query = self.global_query_entry.get().strip()
        if not query:
            print("全局查询内容为空。")
            for client in self.json_clients:
                client._local_json_query("")
            Messagebox.show_info(title='全局查询',message="'全局查询' 条件不得为空。")
            return

        print(f"执行全局查询: '{query}'")
        for client in self.json_clients:
            client._local_json_query(query)

    def perform_global_json(self):
        error_window_ids=[]
        if len(self.json_clients)==0:
            Messagebox.show_error(title='JSON 序列化',message="客户端为空，不可'JSON序列化'。")
        else:
            for client in self.json_clients:
                msg=client.json_serializable()
                if msg['status']=='error':
                    error_window_ids.append(msg['window_id'])
        if len(error_window_ids)>0:
            Messagebox.show_error(title='JSON 序列化',
                                  message=f"【Window{error_window_ids}】 JSON 序列化失败，填写数据格式异常。")

if __name__ == "__main__":
    app = Comparison()
    app.mainloop()