from __future__ import annotations

import tkinter as tk

from model import AlgorithmComparison, IDLE_PID, ScheduleResult


class TimelineGanttCanvas(tk.Canvas):
    def __init__(self, master: tk.Misc, *, height: int = 120) -> None:
        super().__init__(master, height=height, background="white", highlightthickness=1)
        self._result: ScheduleResult | None = None
        self._visible_until: int | None = None
        self.bind("<Configure>", self._redraw)

    def show(self, result: ScheduleResult | None, visible_until: int | None = None) -> None:
        self._result = result
        self._visible_until = visible_until
        self._redraw()

    def _redraw(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        self.delete("all")
        if self._result is None or not self._result.segments:
            self.create_text(12, 12, anchor="nw", text="Chưa có Gantt Chart")
            return

        segments = self._result.segments
        total_end = max(1, segments[-1].end)
        visible_until = total_end if self._visible_until is None else self._visible_until
        width = max(self.winfo_width(), 560)
        left, right, top, height = 45, 20, 24, 48
        usable = max(100, width - left - right)
        fills = ("#f2f2f2", "#dedede", "#cfcfcf", "#bfbfbf", "#e8e8e8")

        for index, segment in enumerate(segments):
            if segment.start >= visible_until:
                continue
            clipped_end = min(segment.end, visible_until)
            x1 = left + (segment.start / total_end) * usable
            x2 = left + (clipped_end / total_end) * usable
            if x2 <= x1:
                continue
            fill = "#fafafa" if segment.pid == IDLE_PID else fills[index % len(fills)]
            self.create_rectangle(x1, top, x2, top + height, fill=fill, outline="black")
            if x2 - x1 >= 28:
                self.create_text((x1 + x2) / 2, top + height / 2, text=segment.pid)
            self.create_text(x1, top + height + 9, anchor="n", text=str(segment.start))

        final_time = min(visible_until, total_end)
        final_x = left + (final_time / total_end) * usable
        self.create_text(final_x, top + height + 9, anchor="n", text=str(final_time))


class ComparisonGanttCanvas(tk.Canvas):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, height=390, background="white", highlightthickness=1)
        self._items: tuple[AlgorithmComparison, ...] = ()
        self._visible_until = 0
        self._total_end = 1
        self.bind("<Configure>", self._redraw)

    def show(self, items: tuple[AlgorithmComparison, ...], visible_until: int) -> None:
        self._items = items
        self._visible_until = visible_until
        self._total_end = max(
            (item.result.segments[-1].end for item in items if item.result.segments),
            default=1,
        )
        self.configure(height=max(250, 72 * len(items) + 38))
        self._redraw()

    def _redraw(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        self.delete("all")
        if not self._items:
            self.create_text(12, 12, anchor="nw", text="Chưa chạy comparison")
            return

        width = max(self.winfo_width(), 780)
        left, right = 190, 25
        usable = max(200, width - left - right)
        row_height, bar_height, top = 68, 34, 20
        fills = ("#f1f1f1", "#dddddd", "#c9c9c9", "#e8e8e8", "#bdbdbd")

        for row, item in enumerate(self._items):
            y = top + row * row_height
            self.create_text(
                10,
                y + bar_height / 2,
                anchor="w",
                text=item.name,
                font=("TkDefaultFont", 9, "bold"),
            )
            for index, segment in enumerate(item.result.segments):
                if segment.start >= self._visible_until:
                    continue
                clipped_end = min(segment.end, self._visible_until)
                x1 = left + (segment.start / self._total_end) * usable
                x2 = left + (clipped_end / self._total_end) * usable
                if x2 <= x1:
                    continue
                fill = "#fafafa" if segment.pid == IDLE_PID else fills[index % len(fills)]
                self.create_rectangle(x1, y, x2, y + bar_height, fill=fill, outline="black")
                if x2 - x1 >= 26:
                    self.create_text((x1 + x2) / 2, y + bar_height / 2, text=segment.pid)

        axis_y = top + len(self._items) * row_height - 18
        tick_step = 1 if self._total_end <= 20 else max(1, self._total_end // 10)
        for tick in range(0, self._total_end + 1, tick_step):
            x = left + (tick / self._total_end) * usable
            self.create_line(x, axis_y, x, axis_y + 5)
            self.create_text(x, axis_y + 7, anchor="n", text=str(tick))

        if self._visible_until <= self._total_end:
            x = left + (self._visible_until / self._total_end) * usable
            self.create_line(x, top - 8, x, axis_y, width=2, dash=(4, 3))
