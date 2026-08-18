from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from service.misc.scheduling import (
    ALGORITHM_LABELS,
    AlgorithmComparison,
    AlgorithmKey,
    SimulationRun,
    build_comparison,
    simulate_algorithm,
)
from model import GanttSegment, IDLE_PID, Process, ScheduleResult
from service.module.module1_nhaplieu import tao_tien_trinh
from service.module.module5_bangketqua import build_result_view_data
from service.module.module6_ganttchart import (
    ComparisonGanttCanvas as SharedComparisonGanttCanvas,
    TimelineGanttCanvas as SharedTimelineGanttCanvas,
)


DETAIL_ALGORITHMS = ("Priority", "FCFS")


def _detail_algorithm_key(label: str, priority_mode: str) -> AlgorithmKey:
    if label == "FCFS":
        return "fcfs"
    if label == "Priority":
        return (
            "priority_preemptive"
            if priority_mode == "Preemptive"
            else "priority_non_preemptive"
        )
    raise ValueError(f"Thuật toán Detail Simulation không hợp lệ: {label}")


def _running_at(result: ScheduleResult, time_point: int) -> str:
    for segment in result.segments:
        if segment.start <= time_point < segment.end:
            return segment.pid
    return "-"


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

        final_x = left + (min(visible_until, total_end) / total_end) * usable
        self.create_text(final_x, top + height + 9, anchor="n", text=str(min(visible_until, total_end)))


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
        row_height = 68
        bar_height = 34
        top = 20
        fills = ("#f1f1f1", "#dddddd", "#c9c9c9", "#e8e8e8", "#bdbdbd")

        for row, item in enumerate(self._items):
            y = top + row * row_height
            self.create_text(10, y + bar_height / 2, anchor="w", text=item.name, font=("TkDefaultFont", 9, "bold"))
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


class SchedulingDemoV2(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CPU Scheduling Simulator - Detail & Comparison")
        self.geometry("1280x900")
        self.minsize(1080, 760)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._detail_run: SimulationRun | None = None
        self._detail_index = 0
        self._detail_after_id: str | None = None
        self._detail_playing = False

        self._comparison_items: tuple[AlgorithmComparison, ...] = ()
        self._comparison_time = 0
        self._comparison_end = 0
        self._comparison_after_id: str | None = None
        self._comparison_playing = False

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        self._build_input()
        self._build_workspace()
        self._load_example()

    def _build_header(self) -> None:
        frame = ttk.Frame(self, padding=(12, 10, 12, 4))
        frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            frame,
            text="CPU Scheduling Simulator",
            font=("TkDefaultFont", 17, "bold"),
        ).pack(side="left")
        ttk.Label(
            frame,
            text="Detail Simulation + Same Tasks / Same Clock Comparison",
        ).pack(side="right")

    def _build_input(self) -> None:
        box = ttk.LabelFrame(self, text="Process Input", padding=8)
        box.grid(row=1, column=0, sticky="ew", padx=12, pady=(6, 8))
        box.columnconfigure(0, weight=1)

        columns = ("pid", "arrival", "burst", "priority")
        self.process_table = ttk.Treeview(box, columns=columns, show="headings", height=5)
        for column, heading, width in (
            ("pid", "PID", 90),
            ("arrival", "Arrival Time", 115),
            ("burst", "Burst Time", 115),
            ("priority", "Priority", 100),
        ):
            self.process_table.heading(column, text=heading)
            self.process_table.column(column, width=width, anchor="center", stretch=True)
        self.process_table.grid(row=0, column=0, columnspan=10, sticky="ew", pady=(0, 7))

        self.pid_var = tk.StringVar()
        self.arrival_var = tk.StringVar()
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar()
        fields = (
            ("PID", self.pid_var),
            ("AT", self.arrival_var),
            ("BT", self.burst_var),
            ("Priority", self.priority_var),
        )
        for index, (label, variable) in enumerate(fields):
            base = index * 2
            ttk.Label(box, text=label).grid(row=1, column=base, sticky="e", padx=(0, 4))
            ttk.Entry(box, textvariable=variable, width=10).grid(row=1, column=base + 1, sticky="ew", padx=(0, 8))
            box.columnconfigure(base + 1, weight=1)

        button_bar = ttk.Frame(box)
        button_bar.grid(row=1, column=8, columnspan=2, sticky="e")
        ttk.Button(button_bar, text="Add", command=self._add_process).pack(side="left")
        ttk.Button(button_bar, text="Delete", command=self._delete_selected).pack(side="left", padx=4)
        ttk.Button(button_bar, text="Example", command=self._load_example).pack(side="left")
        ttk.Button(button_bar, text="Clear", command=self._clear_processes).pack(side="left", padx=(4, 0))

    def _build_workspace(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.detail_tab = ttk.Frame(notebook, padding=10)
        self.comparison_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.detail_tab, text="1. Detail Simulation")
        notebook.add(self.comparison_tab, text="2. Detail Comparison")

        self._build_detail_tab()
        self._build_comparison_tab()

    def _build_detail_tab(self) -> None:
        tab = self.detail_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(3, weight=1)

        controls = ttk.LabelFrame(tab, text="Algorithm & Playback", padding=8)
        controls.grid(row=0, column=0, sticky="ew")
        for column in (1, 3, 5, 7):
            controls.columnconfigure(column, weight=1)

        ttk.Label(controls, text="Algorithm").grid(row=0, column=0, sticky="w")
        self.detail_algorithm_var = tk.StringVar(value="Priority")
        ttk.Combobox(
            controls,
            textvariable=self.detail_algorithm_var,
            values=DETAIL_ALGORITHMS,
            state="readonly",
            width=14,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 12))

        ttk.Label(controls, text="Priority Mode").grid(row=0, column=2, sticky="w")
        self.detail_priority_mode_var = tk.StringVar(value="Preemptive")
        ttk.Combobox(
            controls,
            textvariable=self.detail_priority_mode_var,
            values=("Preemptive", "Non-Preemptive"),
            state="readonly",
            width=16,
        ).grid(row=0, column=3, sticky="ew", padx=(4, 12))

        self.detail_aging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Aging", variable=self.detail_aging_var).grid(row=0, column=4, sticky="w")
        self.detail_aging_interval_var = tk.StringVar(value="5")
        ttk.Entry(controls, textvariable=self.detail_aging_interval_var, width=7).grid(row=0, column=5, sticky="w", padx=(4, 12))

        ttk.Label(controls, text="Speed").grid(row=0, column=6, sticky="w")
        self.detail_speed_var = tk.StringVar(value="1x")
        ttk.Combobox(
            controls,
            textvariable=self.detail_speed_var,
            values=("0.5x", "1x", "2x", "5x"),
            width=7,
            state="readonly",
        ).grid(row=0, column=7, sticky="w", padx=(4, 12))

        ttk.Button(controls, text="Prepare", command=self._prepare_detail).grid(row=0, column=8, padx=(0, 5))
        ttk.Button(controls, text="◀ Previous", command=self._detail_previous).grid(row=0, column=9, padx=3)
        self.detail_play_button = ttk.Button(controls, text="▶ Play", command=self._detail_toggle_play)
        self.detail_play_button.grid(row=0, column=10, padx=3)
        ttk.Button(controls, text="Next ▶", command=self._detail_next).grid(row=0, column=11, padx=(3, 0))

        status = ttk.LabelFrame(tab, text="Current Scheduler State", padding=8)
        status.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        status.columnconfigure(5, weight=1)
        self.detail_time_label = ttk.Label(status, text="TIME: -", font=("TkDefaultFont", 11, "bold"))
        self.detail_time_label.grid(row=0, column=0, sticky="w", padx=(0, 18))
        ttk.Label(status, text="EVENT:").grid(row=0, column=1, sticky="w")
        self.detail_event_label = ttk.Label(status, text="-")
        self.detail_event_label.grid(row=0, column=2, sticky="w", padx=(5, 18))
        ttk.Label(status, text="CPU:").grid(row=0, column=3, sticky="w")
        self.detail_cpu_label = ttk.Label(status, text="-", font=("TkDefaultFont", 12, "bold"))
        self.detail_cpu_label.grid(row=0, column=4, sticky="w", padx=(5, 18))
        self.detail_progress_label = ttk.Label(status, text="Step 0/0")
        self.detail_progress_label.grid(row=0, column=5, sticky="e")

        center = ttk.Frame(tab)
        center.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        center.columnconfigure(0, weight=1)
        center.columnconfigure(1, weight=3)
        center.rowconfigure(0, weight=1)

        queue_box = ttk.LabelFrame(center, text="Ready Queue", padding=7)
        queue_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        queue_box.columnconfigure(0, weight=1)
        queue_box.rowconfigure(0, weight=1)
        queue_columns = ("pid", "remaining", "priority", "effective")
        self.ready_table = ttk.Treeview(queue_box, columns=queue_columns, show="headings", height=8)
        for column, heading in zip(queue_columns, ("PID", "Remaining", "PR", "Effective PR")):
            self.ready_table.heading(column, text=heading)
            self.ready_table.column(column, width=78, anchor="center", stretch=True)
        self.ready_table.grid(row=0, column=0, sticky="nsew")

        visual_box = ttk.LabelFrame(center, text="Step-by-step Execution", padding=7)
        visual_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        visual_box.columnconfigure(0, weight=1)
        visual_box.rowconfigure(2, weight=1)
        self.detail_gantt = SharedTimelineGanttCanvas(visual_box)
        self.detail_gantt.grid(row=0, column=0, sticky="ew")
        ttk.Label(visual_box, text="Explanation").grid(row=1, column=0, sticky="w", pady=(6, 2))
        self.detail_text = tk.Text(visual_box, wrap="word", height=5, state="disabled")
        self.detail_text.grid(row=2, column=0, sticky="nsew")

        result_box = ttk.LabelFrame(tab, text="Final Metrics (hiện đầy đủ khi simulation kết thúc)", padding=7)
        result_box.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        result_box.columnconfigure(0, weight=1)
        result_box.rowconfigure(1, weight=1)
        self.detail_summary_label = ttk.Label(result_box, text="Chưa hoàn tất simulation")
        self.detail_summary_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        metric_columns = ("pid", "at", "bt", "pr", "ct", "tat", "wt", "rt")
        self.detail_metrics_table = ttk.Treeview(result_box, columns=metric_columns, show="headings", height=6)
        for column, heading in zip(metric_columns, ("PID", "AT", "BT", "PR", "CT", "TAT", "WT", "RT")):
            self.detail_metrics_table.heading(column, text=heading)
            self.detail_metrics_table.column(column, width=80, anchor="center", stretch=True)
        self.detail_metrics_table.grid(row=1, column=0, sticky="nsew")

    def _build_comparison_tab(self) -> None:
        tab = self.comparison_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        controls = ttk.LabelFrame(tab, text="Same Tasks / Same Clock", padding=8)
        controls.grid(row=0, column=0, sticky="ew")
        for column in (1, 3, 5, 7):
            controls.columnconfigure(column, weight=1)

        ttk.Label(controls, text="Priority mode").grid(row=0, column=0, sticky="w")
        self.compare_priority_mode_var = tk.StringVar(value="Preemptive")
        ttk.Combobox(
            controls,
            textvariable=self.compare_priority_mode_var,
            values=("Preemptive", "Non-Preemptive"),
            width=17,
            state="readonly",
        ).grid(row=0, column=1, sticky="w", padx=(4, 12))

        self.compare_aging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Priority Aging", variable=self.compare_aging_var).grid(row=0, column=2, sticky="w")
        self.compare_aging_interval_var = tk.StringVar(value="5")
        ttk.Entry(controls, textvariable=self.compare_aging_interval_var, width=7).grid(row=0, column=3, sticky="w", padx=(4, 12))

        ttk.Label(controls, text="RR Quantum").grid(row=0, column=4, sticky="w")
        self.compare_quantum_var = tk.StringVar(value="2")
        ttk.Entry(controls, textvariable=self.compare_quantum_var, width=7).grid(row=0, column=5, sticky="w", padx=(4, 12))

        ttk.Label(controls, text="Speed").grid(row=0, column=6, sticky="w")
        self.compare_speed_var = tk.StringVar(value="1x")
        ttk.Combobox(
            controls,
            textvariable=self.compare_speed_var,
            values=("0.5x", "1x", "2x", "5x"),
            width=7,
            state="readonly",
        ).grid(row=0, column=7, sticky="w", padx=(4, 12))

        ttk.Button(controls, text="Prepare 5 Algorithms", command=self._prepare_comparison).grid(row=0, column=8, padx=(0, 5))
        ttk.Button(controls, text="◀", command=self._comparison_previous).grid(row=0, column=9, padx=2)
        self.compare_play_button = ttk.Button(controls, text="▶ Play", command=self._comparison_toggle_play)
        self.compare_play_button.grid(row=0, column=10, padx=2)
        ttk.Button(controls, text="▶", command=self._comparison_next).grid(row=0, column=11, padx=(2, 0))

        state = ttk.Frame(tab, padding=(0, 7, 0, 0))
        state.grid(row=1, column=0, sticky="ew")
        self.compare_time_label = ttk.Label(state, text="TIME: -", font=("TkDefaultFont", 11, "bold"))
        self.compare_time_label.pack(side="left")
        ttk.Label(
            state,
            text="FCFS | SJF | SRTF | Priority | Round Robin chạy trên cùng process input",
        ).pack(side="right")

        body = ttk.Frame(tab)
        body.grid(row=2, column=0, sticky="nsew", pady=(7, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.compare_gantt = SharedComparisonGanttCanvas(body)
        self.compare_gantt.grid(row=0, column=0, sticky="nsew")

        lower = ttk.Frame(tab)
        lower.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        lower.columnconfigure(0, weight=2)
        lower.columnconfigure(1, weight=1)

        metrics_box = ttk.LabelFrame(lower, text="Comparison Metrics", padding=7)
        metrics_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        metrics_box.columnconfigure(0, weight=1)
        compare_columns = ("algorithm", "running", "wt", "tat", "rt", "switches")
        self.compare_metrics_table = ttk.Treeview(metrics_box, columns=compare_columns, show="headings", height=6)
        headings = ("Algorithm", "Running", "Avg WT", "Avg TAT", "Avg RT", "Context Switch")
        widths = (210, 75, 85, 85, 85, 105)
        for column, heading, width in zip(compare_columns, headings, widths):
            self.compare_metrics_table.heading(column, text=heading)
            self.compare_metrics_table.column(column, width=width, anchor="center", stretch=True)
        self.compare_metrics_table.grid(row=0, column=0, sticky="ew")

        analysis_box = ttk.LabelFrame(lower, text="Evaluation", padding=7)
        analysis_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        analysis_box.columnconfigure(0, weight=1)
        self.compare_analysis_text = tk.Text(analysis_box, wrap="word", height=8, state="disabled")
        self.compare_analysis_text.grid(row=0, column=0, sticky="nsew")

    def _load_example(self) -> None:
        self._clear_processes()
        sample = (
            Process("P1", 0, 5, 3),
            Process("P2", 1, 2, 1),
            Process("P3", 2, 1, 2),
            Process("P4", 4, 3, 2),
        )
        for process in sample:
            self.process_table.insert(
                "",
                "end",
                values=(process.pid, process.arrival, process.burst, process.priority),
            )
        self._reset_detail_view()
        self._reset_comparison_view()

    def _clear_processes(self) -> None:
        for item in self.process_table.get_children():
            self.process_table.delete(item)
        if hasattr(self, "detail_tab"):
            self._reset_detail_view()
            self._reset_comparison_view()

    def _delete_selected(self) -> None:
        for item in self.process_table.selection():
            self.process_table.delete(item)
        self._reset_detail_view()
        self._reset_comparison_view()

    def _add_process(self) -> None:
        try:
            process = tao_tien_trinh(
                self.pid_var.get(),
                int(self.arrival_var.get()),
                int(self.burst_var.get()),
                int(self.priority_var.get()),
            )
        except ValueError as error:
            messagebox.showerror("Input không hợp lệ", str(error), parent=self)
            return

        existing = {
            str(self.process_table.item(item, "values")[0]).casefold()
            for item in self.process_table.get_children()
        }
        if process.pid.casefold() in existing:
            messagebox.showerror("PID bị trùng", f"Đã tồn tại {process.pid}.", parent=self)
            return

        self.process_table.insert(
            "",
            "end",
            values=(process.pid, process.arrival, process.burst, process.priority),
        )
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("")
        self._reset_detail_view()
        self._reset_comparison_view()

    def _collect_processes(self) -> tuple[Process, ...]:
        processes: list[Process] = []
        for item in self.process_table.get_children():
            values = self.process_table.item(item, "values")
            processes.append(
                tao_tien_trinh(
                    str(values[0]),
                    int(values[1]),
                    int(values[2]),
                    int(values[3]),
                )
            )
        if not processes:
            raise ValueError("Cần ít nhất một process để mô phỏng.")
        return tuple(processes)

    def _detail_options(self) -> tuple[AlgorithmKey, int | None]:
        label = self.detail_algorithm_var.get()
        algorithm = _detail_algorithm_key(label, self.detail_priority_mode_var.get())
        aging: int | None = None
        if self.detail_aging_var.get() and algorithm.startswith("priority"):
            aging = int(self.detail_aging_interval_var.get())
            if aging <= 0:
                raise ValueError("Aging Interval phải > 0.")
        return algorithm, aging

    def _prepare_detail(self) -> None:
        self._stop_detail_playback()
        try:
            processes = self._collect_processes()
            algorithm, aging = self._detail_options()
            self._detail_run = simulate_algorithm(
                processes,
                algorithm,
                aging_interval=aging,
            )
        except (ValueError, KeyError) as error:
            messagebox.showerror("Không thể chuẩn bị simulation", str(error), parent=self)
            return

        self._detail_index = 0
        self._render_detail()

    def _render_detail(self) -> None:
        run = self._detail_run
        if run is None or not run.steps:
            self._reset_detail_view(clear_run=False)
            return

        self._detail_index = max(0, min(self._detail_index, len(run.steps) - 1))
        step = run.steps[self._detail_index]
        self.detail_time_label.configure(text=f"TIME: {step.start} → {step.end}")
        self.detail_event_label.configure(text=step.event)
        self.detail_cpu_label.configure(text=step.running)
        self.detail_progress_label.configure(text=f"Step {self._detail_index + 1}/{len(run.steps)}")
        self.detail_gantt.show(run.result, visible_until=step.end)

        for item in self.ready_table.get_children():
            self.ready_table.delete(item)
        for ready in step.ready:
            self.ready_table.insert(
                "",
                "end",
                values=(ready.pid, ready.remaining, ready.priority, ready.effective_priority),
            )

        explanation = (
            f"Algorithm: {run.result.algorithm}\n"
            f"Event: {step.event}\n"
            f"CPU: {step.running}\n"
            f"{step.detail}"
        )
        self._set_text(self.detail_text, explanation)

        if self._detail_index == len(run.steps) - 1:
            self._show_detail_metrics(run.result)
        else:
            self._clear_detail_metrics()

    def _show_detail_metrics(self, result: ScheduleResult) -> None:
        view_data = build_result_view_data(result)
        self.detail_summary_label.configure(
            text=view_data["summary"]
        )
        for item in self.detail_metrics_table.get_children():
            self.detail_metrics_table.delete(item)
        for metric in view_data["metrics"]:
            self.detail_metrics_table.insert(
                "",
                "end",
                values=(
                    metric["pid"],
                    metric["arrival"],
                    metric["burst"],
                    metric["priority"],
                    metric["completion"],
                    metric["turnaround"],
                    metric["waiting"],
                    metric["response"],
                ),
            )

    def _clear_detail_metrics(self) -> None:
        self.detail_summary_label.configure(text="Simulation đang chạy — metrics cuối chưa được công bố")
        for item in self.detail_metrics_table.get_children():
            self.detail_metrics_table.delete(item)

    def _detail_previous(self) -> None:
        self._stop_detail_playback()
        if self._detail_run is None:
            self._prepare_detail()
            return
        self._detail_index = max(0, self._detail_index - 1)
        self._render_detail()

    def _detail_next(self) -> None:
        self._stop_detail_playback()
        if self._detail_run is None:
            self._prepare_detail()
            return
        self._detail_index = min(len(self._detail_run.steps) - 1, self._detail_index + 1)
        self._render_detail()

    def _detail_toggle_play(self) -> None:
        if self._detail_playing:
            self._stop_detail_playback()
            return
        if self._detail_run is None:
            self._prepare_detail()
        if self._detail_run is None:
            return
        if self._detail_index >= len(self._detail_run.steps) - 1:
            self._detail_index = 0
            self._render_detail()
        self._detail_playing = True
        self.detail_play_button.configure(text="⏸ Pause")
        self._schedule_detail_tick()

    def _schedule_detail_tick(self) -> None:
        if not self._detail_playing or self._detail_run is None:
            return
        if self._detail_index >= len(self._detail_run.steps) - 1:
            self._stop_detail_playback()
            return
        delay = self._playback_delay(self.detail_speed_var.get())
        self._detail_after_id = self.after(delay, self._detail_tick)

    def _detail_tick(self) -> None:
        self._detail_after_id = None
        if not self._detail_playing or self._detail_run is None:
            return
        self._detail_index += 1
        self._render_detail()
        self._schedule_detail_tick()

    def _stop_detail_playback(self) -> None:
        self._detail_playing = False
        self.detail_play_button.configure(text="▶ Play")
        if self._detail_after_id is not None:
            self.after_cancel(self._detail_after_id)
            self._detail_after_id = None

    def _reset_detail_view(self, *, clear_run: bool = True) -> None:
        if not hasattr(self, "detail_play_button"):
            return
        self._stop_detail_playback()
        if clear_run:
            self._detail_run = None
        self._detail_index = 0
        self.detail_time_label.configure(text="TIME: -")
        self.detail_event_label.configure(text="-")
        self.detail_cpu_label.configure(text="-")
        self.detail_progress_label.configure(text="Step 0/0")
        self.detail_gantt.show(None)
        for item in self.ready_table.get_children():
            self.ready_table.delete(item)
        self._set_text(self.detail_text, "Chọn thuật toán và nhấn Prepare để xem scheduler chạy từng bước.")
        self._clear_detail_metrics()

    def _prepare_comparison(self) -> None:
        self._stop_comparison_playback()
        try:
            processes = self._collect_processes()
            quantum = int(self.compare_quantum_var.get())
            if quantum <= 0:
                raise ValueError("Time Quantum phải > 0.")
            aging: int | None = None
            if self.compare_aging_var.get():
                aging = int(self.compare_aging_interval_var.get())
                if aging <= 0:
                    raise ValueError("Aging Interval phải > 0.")
            self._comparison_items = build_comparison(
                processes,
                priority_preemptive=self.compare_priority_mode_var.get() == "Preemptive",
                aging_interval=aging,
                quantum=quantum,
            )
        except ValueError as error:
            messagebox.showerror("Không thể chuẩn bị comparison", str(error), parent=self)
            return

        self._comparison_time = 0
        self._comparison_end = max(
            item.result.segments[-1].end
            for item in self._comparison_items
            if item.result.segments
        )
        self._render_comparison()

    def _render_comparison(self) -> None:
        if not self._comparison_items:
            self._reset_comparison_view(clear_items=False)
            return

        self._comparison_time = max(0, min(self._comparison_time, self._comparison_end))
        self.compare_time_label.configure(text=f"TIME: {self._comparison_time}/{self._comparison_end}")
        self.compare_gantt.show(self._comparison_items, self._comparison_time)

        for item in self.compare_metrics_table.get_children():
            self.compare_metrics_table.delete(item)

        finished = self._comparison_time >= self._comparison_end
        sample_time = max(0, self._comparison_time - 1)
        for comparison in self._comparison_items:
            result = comparison.result
            running = "Finished" if finished else _running_at(result, sample_time)
            self.compare_metrics_table.insert(
                "",
                "end",
                values=(
                    comparison.name,
                    running,
                    f"{result.average_waiting:.2f}" if finished else "—",
                    f"{result.average_turnaround:.2f}" if finished else "—",
                    f"{result.average_response:.2f}" if finished else "—",
                    result.context_switches if finished else "—",
                ),
            )

        if finished:
            self._show_comparison_analysis()
        else:
            self._set_text(
                self.compare_analysis_text,
                "Các thuật toán đang chạy trên cùng một clock. Metrics cuối sẽ hiện khi timeline hoàn tất.",
            )

    def _show_comparison_analysis(self) -> None:
        results = [item.result for item in self._comparison_items]
        best_wt = min(results, key=lambda result: result.average_waiting)
        best_tat = min(results, key=lambda result: result.average_turnaround)
        best_rt = min(results, key=lambda result: result.average_response)
        fcfs = next(result for result in results if result.algorithm == "FCFS")
        priority = next(result for result in results if result.algorithm.startswith("Priority"))

        if priority.average_waiting < fcfs.average_waiting:
            delta = fcfs.average_waiting - priority.average_waiting
            percent = 0.0 if fcfs.average_waiting == 0 else delta / fcfs.average_waiting * 100
            priority_vs_fcfs = (
                f"Priority tốt hơn FCFS về Avg WT: {priority.average_waiting:.2f} < "
                f"{fcfs.average_waiting:.2f}, giảm {percent:.2f}%."
            )
        elif priority.average_waiting > fcfs.average_waiting:
            delta = priority.average_waiting - fcfs.average_waiting
            percent = 0.0 if fcfs.average_waiting == 0 else delta / fcfs.average_waiting * 100
            priority_vs_fcfs = (
                f"FCFS tốt hơn Priority về Avg WT: {fcfs.average_waiting:.2f} < "
                f"{priority.average_waiting:.2f}; Priority cao hơn {percent:.2f}%."
            )
        else:
            priority_vs_fcfs = "Priority và FCFS có Avg Waiting Time bằng nhau trên bộ dữ liệu này."

        analysis = (
            "KẾT QUẢ SO SÁNH\n\n"
            f"Best Avg Waiting Time: {best_wt.algorithm} ({best_wt.average_waiting:.2f})\n"
            f"Best Avg Turnaround Time: {best_tat.algorithm} ({best_tat.average_turnaround:.2f})\n"
            f"Best Avg Response Time: {best_rt.algorithm} ({best_rt.average_response:.2f})\n\n"
            f"{priority_vs_fcfs}\n\n"
            "Kết luận chỉ áp dụng cho chính bộ process đang nhập. Một thuật toán không luôn tốt nhất cho mọi workload."
        )
        self._set_text(self.compare_analysis_text, analysis)

    def _comparison_previous(self) -> None:
        self._stop_comparison_playback()
        if not self._comparison_items:
            self._prepare_comparison()
            return
        self._comparison_time = max(0, self._comparison_time - 1)
        self._render_comparison()

    def _comparison_next(self) -> None:
        self._stop_comparison_playback()
        if not self._comparison_items:
            self._prepare_comparison()
            return
        self._comparison_time = min(self._comparison_end, self._comparison_time + 1)
        self._render_comparison()

    def _comparison_toggle_play(self) -> None:
        if self._comparison_playing:
            self._stop_comparison_playback()
            return
        if not self._comparison_items:
            self._prepare_comparison()
        if not self._comparison_items:
            return
        if self._comparison_time >= self._comparison_end:
            self._comparison_time = 0
            self._render_comparison()
        self._comparison_playing = True
        self.compare_play_button.configure(text="⏸ Pause")
        self._schedule_comparison_tick()

    def _schedule_comparison_tick(self) -> None:
        if not self._comparison_playing:
            return
        if self._comparison_time >= self._comparison_end:
            self._stop_comparison_playback()
            return
        delay = self._playback_delay(self.compare_speed_var.get())
        self._comparison_after_id = self.after(delay, self._comparison_tick)

    def _comparison_tick(self) -> None:
        self._comparison_after_id = None
        if not self._comparison_playing:
            return
        self._comparison_time += 1
        self._render_comparison()
        self._schedule_comparison_tick()

    def _stop_comparison_playback(self) -> None:
        self._comparison_playing = False
        if hasattr(self, "compare_play_button"):
            self.compare_play_button.configure(text="▶ Play")
        if self._comparison_after_id is not None:
            self.after_cancel(self._comparison_after_id)
            self._comparison_after_id = None

    def _reset_comparison_view(self, *, clear_items: bool = True) -> None:
        if not hasattr(self, "compare_play_button"):
            return
        self._stop_comparison_playback()
        if clear_items:
            self._comparison_items = ()
        self._comparison_time = 0
        self._comparison_end = 0
        self.compare_time_label.configure(text="TIME: -")
        self.compare_gantt.show((), 0)
        for item in self.compare_metrics_table.get_children():
            self.compare_metrics_table.delete(item)
        self._set_text(
            self.compare_analysis_text,
            "Nhấn Prepare 5 Algorithms để chạy FCFS, SJF, SRTF, Priority và Round Robin trên cùng input.",
        )

    @staticmethod
    def _playback_delay(speed_text: str) -> int:
        speed = float(speed_text.rstrip("x"))
        return max(80, int(700 / speed))

    @staticmethod
    def _set_text(widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _close(self) -> None:
        self._stop_detail_playback()
        self._stop_comparison_playback()
        self.destroy()


def main() -> None:
    app = SchedulingDemoV2()
    app.mainloop()


if __name__ == "__main__":
    main()
