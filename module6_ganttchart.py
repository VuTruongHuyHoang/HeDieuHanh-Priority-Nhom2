import tkinter as tk


class GanttChart:
    def __init__(self, parent):
        self.data = []
        self.visible_until = None
        self.total_time = None

        self.frame = tk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.frame, height=220, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.scroll = tk.Scrollbar(
            self.frame,
            orient="horizontal",
            command=self.canvas.xview,
        )
        self.scroll.pack(side="bottom", fill="x")
        self.canvas.config(xscrollcommand=self.scroll.set)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, _event):
        if self.data:
            self.draw(self.data, self.visible_until, self.total_time)

    def draw(self, data, visible_until=None, total_time=None):
        self.data = [dict(item) for item in data]
        self.visible_until = visible_until
        self.total_time = total_time
        self.canvas.delete("all")

        if not data:
            self.canvas.create_text(
                20,
                20,
                anchor="nw",
                text="Chưa có biểu đồ Gantt",
            )
            return

        left = 50
        y = 70
        height = 60
        data_end = max(item["finish"] for item in data)
        total_time = max(total_time or data_end, data_end, 1)
        if visible_until is None:
            visible_until = total_time
        else:
            visible_until = max(0, min(visible_until, total_time))

        available_width = max(self.canvas.winfo_width() - 100, 600)
        scale = max(30, available_width / total_time)

        for item in data:
            pid = item["pid"]
            start = item["start"]
            if start >= visible_until:
                continue

            finish = min(item["finish"], visible_until)
            x1 = left + start * scale
            x2 = left + finish * scale
            width = x2 - x1

            self.canvas.create_rectangle(
                x1,
                y,
                x2,
                y + height,
                fill="lightgray" if pid == "Idle" else "lightblue",
                outline="black",
            )
            if width >= 25:
                self.canvas.create_text(
                    (x1 + x2) / 2,
                    y + height / 2,
                    text=pid,
                    font=("Arial", 11, "bold"),
                )
            self.canvas.create_text(
                x1,
                y + height + 15,
                text=str(start),
                font=("Arial", 9),
            )

        final_x = left + visible_until * scale
        self.canvas.create_text(
            final_x,
            y + height + 15,
            text=str(visible_until),
            font=("Arial", 9),
        )
        chart_width = left + total_time * scale
        self.canvas.create_text(
            max(450, chart_width / 2),
            25,
            text="BIỂU ĐỒ GANTT",
            font=("Arial", 15, "bold"),
        )
        self.canvas.config(scrollregion=(0, 0, chart_width + 50, 200))
