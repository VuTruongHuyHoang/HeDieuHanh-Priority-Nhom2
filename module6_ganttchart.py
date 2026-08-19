import tkinter as tk


class GanttChart:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.frame,
            height=220,
            bg="white"
        )
        self.canvas.pack(
            side="top",
            fill="both",
            expand=True
        )

        self.scroll = tk.Scrollbar(
            self.frame,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.scroll.pack(
            side="bottom",
            fill="x"
        )

        self.canvas.config(
            xscrollcommand=self.scroll.set
        )

    def draw(self, data):
        self.canvas.delete("all")

        if len(data) == 0:
            return

        x = 50
        y = 70
        height = 60
        scale = 50

        for item in data:
            pid = item["pid"]
            start = item["start"]
            finish = item["finish"]

            width = (finish - start) * scale

            if width < 50:
                width = 50

            self.canvas.create_rectangle(
                x,
                y,
                x + width,
                y + height,
                fill="lightblue",
                outline="black"
            )

            self.canvas.create_text(
                x + width / 2,
                y + height / 2,
                text=pid,
                font=("Arial", 11, "bold")
            )

            self.canvas.create_text(
                x,
                y + height + 15,
                text=str(start),
                font=("Arial", 9)
            )

            x += width

        self.canvas.create_text(
            x,
            y + height + 15,
            text=str(data[-1]["finish"]),
            font=("Arial", 9)
        )

        self.canvas.create_text(
            450,
            25,
            text="BIỂU ĐỒ GANTT",
            font=("Arial", 15, "bold")
        )

        self.canvas.config(
            scrollregion=(0, 0, x + 50, 200)
        )

