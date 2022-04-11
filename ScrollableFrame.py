import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, canvas_width, canvas_height, frame_width, frame_height,
                bar_x = True, bar_y = True):
        super().__init__(container)
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.scrollable_frame = ttk.Frame(self.canvas, width=frame_width, height=frame_height)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        if bar_y:
            self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        if bar_x:
            self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)