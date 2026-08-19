import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from analyze import (
    GRAPH_COLORS,
    GRAPH_METRICS,
    SUMMARY_GRAPH_METRICS,
    analyze_path,
    build_graph_series,
    build_summary_rows,
)
from dummy_data import danh_sach_test
from module1_nhaplieu import ProcessInputManager, chuan_hoa_danh_sach
from module2_nonpreemptive import mo_phong_priority_nonpreemptive
from module3_preemptive import mo_phong_priority_preemptive
from module5_bangketqua import ResultTable
from module6_ganttchart import GanttChart
from module7_fcfs import mo_phong_fcfs


SPEED_DELAYS = {
    "0.5x": 1600,
    "1x": 800,
    "2x": 400,
    "5x": 160,
}

BATCH_GRAPH_VIEWS = {
    "Summary (All Metrics)": None,
    **{title: metric for metric, title in GRAPH_METRICS.items()},
}

def _running_at(gantt, time_point):
    for segment in gantt:
        if segment["start"] <= time_point < segment["finish"]:
            return segment["pid"]
    return "Idle"


class SchedulingDemoV2(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Priority Scheduling Demo V2")
        self.geometry("1220x900")
        self.minsize(980, 720)

        self.input_manager = ProcessInputManager()
        self.input_entries = {}

        self.detail_result = None
        self.detail_index = 0
        self.detail_after_id = None

        self.comparison_results = None
        self.comparison_time = 0
        self.comparison_total_time = 0
        self.comparison_after_id = None

        self._build_header()
        self._build_input()
        self._build_workspace()
        self._load_example()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_header(self):
        ttk.Label(
            self,
            text="MÔ PHỎNG LẬP LỊCH CPU PRIORITY",
            font=("Arial", 18, "bold"),
        ).pack(pady=(10, 4))

    def _build_input(self):
        frame = ttk.LabelFrame(self, text="Process Input - Module 1", padding=8)
        frame.pack(fill="x", padx=10, pady=6)

        form = ttk.Frame(frame)
        form.pack(side="left", padx=(0, 12))
        for column, name in enumerate(("PID", "AT", "BT", "PR")):
            ttk.Label(form, text=name).grid(row=0, column=column, padx=3)
            entry = ttk.Entry(form, width=9)
            entry.grid(row=1, column=column, padx=3, pady=3)
            self.input_entries[name] = entry

        buttons = ttk.Frame(frame)
        buttons.pack(side="left", padx=6)
        ttk.Button(buttons, text="Add", command=self._add_process).grid(row=0, column=0, padx=3)
        ttk.Button(buttons, text="Delete", command=self._delete_selected).grid(row=0, column=1, padx=3)
        ttk.Button(buttons, text="Example", command=self._load_example).grid(row=1, column=0, padx=3, pady=4)
        ttk.Button(buttons, text="Clear", command=self._clear_processes).grid(row=1, column=1, padx=3, pady=4)
        ttk.Button(buttons, text="Load CSV", command=self._load_csv).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=3,
        )

        columns = ("PID", "AT", "BT", "PR")
        self.input_table = ttk.Treeview(frame, columns=columns, show="headings", height=4)
        for column in columns:
            self.input_table.heading(column, text=column)
            self.input_table.column(column, width=72, anchor="center")
        self.input_table.pack(side="left", fill="x", expand=True)

    def _build_workspace(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.detail_tab = ttk.Frame(notebook)
        self.comparison_tab = ttk.Frame(notebook)
        self.batch_tab = ttk.Frame(notebook)
        notebook.add(self.detail_tab, text="Detail Simulation")
        notebook.add(self.comparison_tab, text="Comparison: FCFS vs Priority")
        notebook.add(self.batch_tab, text="Batch Analysis")

        self._build_detail_tab()
        self._build_comparison_tab()
        self._build_batch_tab()

    def _build_detail_tab(self):
        controls = ttk.Frame(self.detail_tab, padding=8)
        controls.pack(fill="x")

        self.detail_algorithm = tk.StringVar(value="Priority")
        self.detail_mode = tk.StringVar(value="Non-Preemptive")
        self.detail_aging = tk.BooleanVar(value=False)
        self.detail_interval = tk.StringVar(value="2")
        self.detail_speed = tk.StringVar(value="1x")

        ttk.Label(controls, text="Algorithm").grid(row=0, column=0, padx=3)
        algorithm_box = ttk.Combobox(
            controls,
            textvariable=self.detail_algorithm,
            values=("Priority", "FCFS"),
            state="readonly",
            width=13,
        )
        algorithm_box.grid(row=1, column=0, padx=3)
        algorithm_box.bind("<<ComboboxSelected>>", self._update_detail_controls)

        ttk.Label(controls, text="Priority Mode").grid(row=0, column=1, padx=3)
        self.detail_mode_box = ttk.Combobox(
            controls,
            textvariable=self.detail_mode,
            values=("Non-Preemptive", "Preemptive"),
            state="readonly",
            width=17,
        )
        self.detail_mode_box.grid(row=1, column=1, padx=3)

        self.detail_aging_check = ttk.Checkbutton(
            controls,
            text="Aging",
            variable=self.detail_aging,
            command=self._update_detail_controls,
        )
        self.detail_aging_check.grid(row=1, column=2, padx=8)

        ttk.Label(controls, text="Interval").grid(row=0, column=3, padx=3)
        self.detail_interval_entry = ttk.Entry(
            controls,
            textvariable=self.detail_interval,
            width=8,
        )
        self.detail_interval_entry.grid(row=1, column=3, padx=3)

        ttk.Label(controls, text="Speed").grid(row=0, column=4, padx=3)
        ttk.Combobox(
            controls,
            textvariable=self.detail_speed,
            values=tuple(SPEED_DELAYS),
            state="readonly",
            width=7,
        ).grid(row=1, column=4, padx=3)

        ttk.Button(controls, text="Prepare", command=self._prepare_detail).grid(
            row=1, column=5, padx=10
        )

        status = ttk.Frame(self.detail_tab, padding=(8, 2))
        status.pack(fill="x")
        self.detail_progress = tk.StringVar(value="Step 0/0")
        self.detail_time = tk.StringVar(value="Time: -")
        self.detail_event = tk.StringVar(value="Event: -")
        self.detail_cpu = tk.StringVar(value="CPU: -")
        for variable in (self.detail_progress, self.detail_time, self.detail_event, self.detail_cpu):
            ttk.Label(status, textvariable=variable).pack(side="left", padx=12)

        playback = ttk.Frame(self.detail_tab, padding=(8, 2))
        playback.pack(fill="x")
        ttk.Button(playback, text="Previous", command=self._detail_previous).pack(side="left", padx=3)
        ttk.Button(playback, text="Next", command=self._detail_next).pack(side="left", padx=3)
        self.detail_play_button = ttk.Button(
            playback,
            text="Play",
            command=self._detail_toggle_play,
        )
        self.detail_play_button.pack(side="left", padx=3)
        ttk.Button(playback, text="Reset", command=self._reset_detail).pack(side="left", padx=3)

        body = ttk.Frame(self.detail_tab, padding=8)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        gantt_box = ttk.LabelFrame(body, text="Gantt Chart - Module 6")
        gantt_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.detail_gantt = GanttChart(gantt_box)
        self.detail_gantt.canvas.configure(height=170)

        ready_box = ttk.LabelFrame(body, text="Ready Queue")
        ready_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        ready_columns = ("PID", "Remaining", "Priority", "Effective")
        self.detail_ready = ttk.Treeview(
            ready_box,
            columns=ready_columns,
            show="headings",
            height=6,
        )
        for column in ready_columns:
            self.detail_ready.heading(column, text=column)
            self.detail_ready.column(column, width=78, anchor="center")
        self.detail_ready.pack(fill="both", expand=True)

        self.detail_text = tk.Text(self.detail_tab, height=3, wrap="word")
        self.detail_text.pack(fill="x", padx=8, pady=(0, 4))
        self.detail_text.configure(state="disabled")

        result_box = ttk.LabelFrame(self.detail_tab, text="Final Metrics - Module 5")
        result_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.detail_result_table = ResultTable(result_box)
        self.detail_result_table.pack(fill="both", expand=True)
        self._update_detail_controls()

    def _build_comparison_tab(self):
        controls = ttk.Frame(self.comparison_tab, padding=8)
        controls.pack(fill="x")

        self.compare_mode = tk.StringVar(value="Non-Preemptive")
        self.compare_aging = tk.BooleanVar(value=False)
        self.compare_interval = tk.StringVar(value="2")
        self.compare_speed = tk.StringVar(value="1x")

        ttk.Label(controls, text="Priority Mode").grid(row=0, column=0, padx=3)
        ttk.Combobox(
            controls,
            textvariable=self.compare_mode,
            values=("Non-Preemptive", "Preemptive"),
            state="readonly",
            width=17,
        ).grid(row=1, column=0, padx=3)

        ttk.Checkbutton(
            controls,
            text="Aging",
            variable=self.compare_aging,
            command=self._update_comparison_controls,
        ).grid(row=1, column=1, padx=8)

        ttk.Label(controls, text="Interval").grid(row=0, column=2, padx=3)
        self.compare_interval_entry = ttk.Entry(
            controls,
            textvariable=self.compare_interval,
            width=8,
        )
        self.compare_interval_entry.grid(row=1, column=2, padx=3)

        ttk.Label(controls, text="Speed").grid(row=0, column=3, padx=3)
        ttk.Combobox(
            controls,
            textvariable=self.compare_speed,
            values=tuple(SPEED_DELAYS),
            state="readonly",
            width=7,
        ).grid(row=1, column=3, padx=3)

        ttk.Button(controls, text="Prepare", command=self._prepare_comparison).grid(
            row=1, column=4, padx=10
        )

        status = ttk.Frame(self.comparison_tab, padding=(8, 2))
        status.pack(fill="x")
        self.compare_time_label = tk.StringVar(value="Time: 0/0")
        self.compare_fcfs_cpu = tk.StringVar(value="FCFS CPU: -")
        self.compare_priority_cpu = tk.StringVar(value="Priority CPU: -")
        for variable in (
            self.compare_time_label,
            self.compare_fcfs_cpu,
            self.compare_priority_cpu,
        ):
            ttk.Label(status, textvariable=variable).pack(side="left", padx=12)

        playback = ttk.Frame(self.comparison_tab, padding=(8, 2))
        playback.pack(fill="x")
        ttk.Button(playback, text="Previous", command=self._comparison_previous).pack(side="left", padx=3)
        ttk.Button(playback, text="Next", command=self._comparison_next).pack(side="left", padx=3)
        self.compare_play_button = ttk.Button(
            playback,
            text="Play",
            command=self._comparison_toggle_play,
        )
        self.compare_play_button.pack(side="left", padx=3)
        ttk.Button(playback, text="Reset", command=self._reset_comparison).pack(side="left", padx=3)

        fcfs_box = ttk.LabelFrame(self.comparison_tab, text="FCFS")
        fcfs_box.pack(fill="both", expand=True, padx=8, pady=4)
        self.compare_fcfs_gantt = GanttChart(fcfs_box)
        self.compare_fcfs_gantt.canvas.configure(height=125)

        priority_box = ttk.LabelFrame(self.comparison_tab, text="Priority")
        priority_box.pack(fill="both", expand=True, padx=8, pady=4)
        self.compare_priority_gantt = GanttChart(priority_box)
        self.compare_priority_gantt.canvas.configure(height=125)

        columns = ("Algorithm", "Avg WT", "Avg TAT", "Avg RT", "Context Switch")
        self.compare_table = ttk.Treeview(
            self.comparison_tab,
            columns=columns,
            show="headings",
            height=2,
        )
        for column in columns:
            self.compare_table.heading(column, text=column)
            self.compare_table.column(column, width=130, anchor="center")
        self.compare_table.pack(fill="x", padx=8, pady=4)

        self.compare_analysis = ttk.Label(self.comparison_tab, text="", anchor="center")
        self.compare_analysis.pack(fill="x", padx=8, pady=(0, 8))
        self._update_comparison_controls()

    def _build_batch_tab(self):
        controls = ttk.LabelFrame(
            self.batch_tab,
            text="Analyze multiple CSV files",
            padding=10,
        )
        controls.pack(fill="x", padx=8, pady=8)
        controls.columnconfigure(1, weight=1)

        self.batch_input_path = tk.StringVar()
        self.batch_output_path = tk.StringVar()
        self.batch_priority_mode = tk.StringVar(value="Both")
        self.batch_aging = tk.BooleanVar(value=False)
        self.batch_interval = tk.StringVar(value="2")
        self.batch_graph_view = tk.StringVar(value="Summary (All Metrics)")
        self.batch_graph_hint = tk.StringVar(
            value="Average metrics aggregated across all successful CSV files"
        )
        self.batch_graph_rows = []
        self.batch_status = tk.StringVar(
            value="Select a folder containing CSV files to begin."
        )

        ttk.Label(controls, text="CSV folder").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        ttk.Entry(controls, textvariable=self.batch_input_path).grid(
            row=0, column=1, sticky="ew", pady=4
        )
        ttk.Button(
            controls,
            text="Browse",
            command=self._browse_batch_input,
        ).grid(row=0, column=2, padx=(8, 0), pady=4)

        ttk.Label(controls, text="Output folder").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        ttk.Entry(controls, textvariable=self.batch_output_path).grid(
            row=1, column=1, sticky="ew", pady=4
        )
        ttk.Button(
            controls,
            text="Browse",
            command=self._browse_batch_output,
        ).grid(row=1, column=2, padx=(8, 0), pady=4)

        options = ttk.Frame(controls)
        options.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 2))
        ttk.Label(options, text="Priority mode").grid(row=0, column=0, padx=(0, 5))
        ttk.Combobox(
            options,
            textvariable=self.batch_priority_mode,
            values=("Both", "Non-Preemptive", "Preemptive"),
            state="readonly",
            width=17,
        ).grid(row=0, column=1, padx=(0, 12))
        ttk.Checkbutton(
            options,
            text="Aging",
            variable=self.batch_aging,
            command=self._update_batch_controls,
        ).grid(row=0, column=2, padx=4)
        ttk.Label(options, text="Interval").grid(row=0, column=3, padx=(8, 4))
        self.batch_interval_entry = ttk.Entry(
            options,
            textvariable=self.batch_interval,
            width=8,
        )
        self.batch_interval_entry.grid(row=0, column=4, padx=(0, 12))
        ttk.Button(
            options,
            text="Analyze and save",
            command=self._run_batch_analysis,
        ).grid(row=0, column=5, padx=4)

        result_box = ttk.LabelFrame(
            self.batch_tab,
            text="FCFS and Priority statistics",
            padding=8,
        )
        result_box.pack(fill="x", padx=8, pady=(0, 8))
        result_box.columnconfigure(0, weight=1)
        result_box.rowconfigure(0, weight=1)

        columns = (
            "Dataset",
            "Algorithm",
            "Avg WT",
            "Avg TAT",
            "Avg RT",
            "Context Switch",
            "Total Time",
            "Status",
        )
        self.batch_table = ttk.Treeview(
            result_box,
            columns=columns,
            show="headings",
            height=7,
        )
        for column in columns:
            self.batch_table.heading(column, text=column)
            width = 190 if column in {"Dataset", "Algorithm"} else 105
            self.batch_table.column(column, width=width, anchor="center")
        scrollbar = ttk.Scrollbar(
            result_box,
            orient="vertical",
            command=self.batch_table.yview,
        )
        self.batch_table.configure(yscrollcommand=scrollbar.set)
        self.batch_table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        graph_box = ttk.LabelFrame(
            self.batch_tab,
            text="FCFS and Priority graph",
            padding=8,
        )
        graph_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        graph_box.columnconfigure(0, weight=1)
        graph_box.rowconfigure(1, weight=1)

        graph_controls = ttk.Frame(graph_box)
        graph_controls.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ttk.Label(graph_controls, text="Graph view").pack(side="left", padx=(0, 5))
        graph_view_box = ttk.Combobox(
            graph_controls,
            textvariable=self.batch_graph_view,
            values=tuple(BATCH_GRAPH_VIEWS),
            state="readonly",
            width=28,
        )
        graph_view_box.pack(side="left", padx=(0, 12))
        graph_view_box.bind("<<ComboboxSelected>>", self._draw_batch_graph)
        ttk.Label(
            graph_controls,
            textvariable=self.batch_graph_hint,
        ).pack(side="left")

        canvas_frame = ttk.Frame(graph_box)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.batch_graph_canvas = tk.Canvas(
            canvas_frame,
            height=260,
            background="white",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
        )
        graph_scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="horizontal",
            command=self.batch_graph_canvas.xview,
        )
        self.batch_graph_canvas.configure(xscrollcommand=graph_scrollbar.set)
        self.batch_graph_canvas.grid(row=0, column=0, sticky="nsew")
        graph_scrollbar.grid(row=1, column=0, sticky="ew")
        self.batch_graph_canvas.bind("<Configure>", self._draw_batch_graph)

        ttk.Label(
            self.batch_tab,
            textvariable=self.batch_status,
            anchor="w",
            wraplength=1150,
        ).pack(fill="x", padx=10, pady=(0, 10))
        self._update_batch_controls()

    def _refresh_input_table(self):
        for item in self.input_table.get_children():
            self.input_table.delete(item)
        for process in self.input_manager.get_data():
            self.input_table.insert(
                "",
                "end",
                values=(process["PID"], process["AT"], process["BT"], process["PR"]),
            )

    def _load_example(self):
        self.input_manager.clear()
        for process in danh_sach_test:
            self.input_manager.add_process(
                process["PID"], process["AT"], process["BT"], process["PR"]
            )
        self._refresh_input_table()
        self._input_changed()

    def _clear_processes(self):
        self.input_manager.clear()
        self._refresh_input_table()
        self._input_changed()

    def _load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file dữ liệu tiến trình",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return

        success, message = self.input_manager.load_from_csv(file_path)
        if not success:
            messagebox.showerror("Không thể tải CSV", message)
            return

        self._refresh_input_table()
        self._input_changed()
        messagebox.showinfo("Load CSV", message)

    def _delete_selected(self):
        selected = self.input_table.selection()
        if not selected:
            messagebox.showinfo("Delete", "Hãy chọn một tiến trình cần xóa.")
            return
        pid = self.input_table.item(selected[0], "values")[0]
        self.input_manager.remove_process(pid)
        self._refresh_input_table()
        self._input_changed()

    def _add_process(self):
        success, message = self.input_manager.add_process(
            self.input_entries["PID"].get(),
            self.input_entries["AT"].get(),
            self.input_entries["BT"].get(),
            self.input_entries["PR"].get(),
        )
        if not success:
            messagebox.showerror("Dữ liệu không hợp lệ", message)
            return
        for entry in self.input_entries.values():
            entry.delete(0, "end")
        self._refresh_input_table()
        self._input_changed()

    def _input_changed(self):
        self._reset_detail()
        self._reset_comparison()

    def _collect_processes(self):
        return chuan_hoa_danh_sach(self.input_manager.get_data())

    @staticmethod
    def _aging_interval(enabled, value):
        if not enabled:
            return None
        interval = int(value)
        if interval <= 0:
            raise ValueError("Aging interval phải lớn hơn 0.")
        return interval

    def _update_detail_controls(self, _event=None):
        is_priority = self.detail_algorithm.get() == "Priority"
        self.detail_mode_box.configure(state="readonly" if is_priority else "disabled")
        self.detail_aging_check.configure(state="normal" if is_priority else "disabled")
        interval_enabled = is_priority and self.detail_aging.get()
        self.detail_interval_entry.configure(state="normal" if interval_enabled else "disabled")

    def _update_comparison_controls(self):
        self.compare_interval_entry.configure(
            state="normal" if self.compare_aging.get() else "disabled"
        )

    def _browse_batch_input(self):
        directory = filedialog.askdirectory(title="Select folder containing CSV files")
        if not directory:
            return
        self.batch_input_path.set(directory)
        if not self.batch_output_path.get().strip():
            self.batch_output_path.set(str(Path(directory) / "analysis_output"))

    def _browse_batch_output(self):
        directory = filedialog.askdirectory(title="Select output folder")
        if directory:
            self.batch_output_path.set(directory)

    def _update_batch_controls(self):
        self.batch_interval_entry.configure(
            state="normal" if self.batch_aging.get() else "disabled"
        )

    def _draw_batch_graph(self, _event=None):
        canvas = self.batch_graph_canvas
        canvas.delete("all")
        if not self.batch_graph_rows:
            canvas.create_text(
                20,
                20,
                anchor="nw",
                text="Run Batch Analysis to display the graph.",
                fill="#666666",
            )
            canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), 260))
            return

        graph_view = self.batch_graph_view.get()
        metric = BATCH_GRAPH_VIEWS.get(graph_view)
        if metric is not None:
            self.batch_graph_hint.set(
                "Metric values of each CSV file, grouped by scheduling algorithm"
            )
            self._draw_batch_metric_graph(metric)
            return

        self.batch_graph_hint.set(
            "Average metrics aggregated across all successful CSV files"
        )

        summary_rows = build_summary_rows(self.batch_graph_rows)
        if not summary_rows:
            canvas.create_text(
                20,
                20,
                anchor="nw",
                text="No successful data is available for this graph.",
                fill="#666666",
            )
            return

        group_width = 240
        content_width = max(
            canvas.winfo_width(),
            100 + len(summary_rows) * group_width,
        )
        height = max(canvas.winfo_height(), 260)
        left = 55
        top = 48
        bottom = height - 85
        plot_height = max(80, bottom - top)
        values = [
            float(row[metric])
            for row in summary_rows
            for metric, _label in SUMMARY_GRAPH_METRICS
        ]
        maximum = max(values, default=0.0)
        y_max = maximum * 1.15 if maximum > 0 else 1.0

        legend_x = left
        for index, (_metric, label) in enumerate(SUMMARY_GRAPH_METRICS):
            color = GRAPH_COLORS[index % len(GRAPH_COLORS)]
            canvas.create_rectangle(
                legend_x,
                12,
                legend_x + 12,
                24,
                fill=color,
                outline="",
            )
            canvas.create_text(
                legend_x + 17,
                18,
                anchor="w",
                text=label,
                font=("Arial", 9),
            )
            legend_x += max(125, len(label) * 7 + 30)

        for tick in range(6):
            value = y_max * tick / 5
            y = bottom - plot_height * tick / 5
            canvas.create_line(left, y, content_width - 20, y, fill="#DDDDDD")
            canvas.create_text(
                left - 7,
                y,
                anchor="e",
                text=f"{value:.1f}",
                font=("Arial", 8),
            )
        canvas.create_line(left, top, left, bottom, fill="#333333", width=2)
        canvas.create_line(
            left,
            bottom,
            content_width - 20,
            bottom,
            fill="#333333",
            width=2,
        )

        bar_width = 30
        for algorithm_index, row in enumerate(summary_rows):
            center = left + 75 + algorithm_index * group_width
            first_x = center - len(SUMMARY_GRAPH_METRICS) * bar_width / 2
            for metric_index, (metric, _label) in enumerate(SUMMARY_GRAPH_METRICS):
                value = float(row[metric])
                color = GRAPH_COLORS[metric_index % len(GRAPH_COLORS)]
                bar_height = value / y_max * plot_height
                x1 = first_x + metric_index * bar_width
                y1 = bottom - bar_height
                canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + bar_width - 3,
                    bottom,
                    fill=color,
                    outline="",
                )
                canvas.create_text(
                    x1 + (bar_width - 3) / 2,
                    y1 - 7,
                    text=f"{value:.2f}",
                    font=("Arial", 8),
                )
            canvas.create_text(
                center,
                bottom + 10,
                anchor="ne",
                angle=15,
                text=row["algorithm"],
                font=("Arial", 8),
            )
            canvas.create_text(
                center,
                bottom + 68,
                text=f"{row['dataset_count']} datasets",
                font=("Arial", 8),
                fill="#666666",
            )

        canvas.configure(scrollregion=(0, 0, content_width, height))

    def _draw_batch_metric_graph(self, metric):
        canvas = self.batch_graph_canvas
        series = build_graph_series(self.batch_graph_rows, metric)
        datasets = series["datasets"]
        algorithms = series["algorithms"]
        if not datasets or not algorithms:
            canvas.create_text(
                20,
                20,
                anchor="nw",
                text="No successful data is available for this graph.",
                fill="#666666",
            )
            canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), 260))
            return

        group_width = max(105, len(algorithms) * 30 + 30)
        content_width = max(
            canvas.winfo_width(),
            100 + len(datasets) * group_width,
        )
        height = max(canvas.winfo_height(), 260)
        left = 55
        top = 48
        bottom = height - 72
        plot_height = max(80, bottom - top)
        values = [
            value
            for dataset_values in series["values"].values()
            for value in dataset_values.values()
        ]
        maximum = max(values, default=0.0)
        y_max = maximum * 1.15 if maximum > 0 else 1.0

        legend_x = left
        for index, algorithm in enumerate(algorithms):
            color = GRAPH_COLORS[index % len(GRAPH_COLORS)]
            canvas.create_rectangle(
                legend_x,
                12,
                legend_x + 12,
                24,
                fill=color,
                outline="",
            )
            canvas.create_text(
                legend_x + 17,
                18,
                anchor="w",
                text=algorithm,
                font=("Arial", 9),
            )
            legend_x += max(155, len(algorithm) * 7 + 32)

        for tick in range(6):
            value = y_max * tick / 5
            y = bottom - plot_height * tick / 5
            canvas.create_line(left, y, content_width - 20, y, fill="#DDDDDD")
            canvas.create_text(
                left - 7,
                y,
                anchor="e",
                text=f"{value:.1f}",
                font=("Arial", 8),
            )
        canvas.create_line(left, top, left, bottom, fill="#333333", width=2)
        canvas.create_line(
            left,
            bottom,
            content_width - 20,
            bottom,
            fill="#333333",
            width=2,
        )

        bar_width = 24
        for dataset_index, dataset in enumerate(datasets):
            center = left + 55 + dataset_index * group_width
            first_x = center - len(algorithms) * bar_width / 2
            for algorithm_index, algorithm in enumerate(algorithms):
                value = series["values"].get(dataset, {}).get(algorithm)
                if value is None:
                    continue
                color = GRAPH_COLORS[algorithm_index % len(GRAPH_COLORS)]
                bar_height = value / y_max * plot_height
                x1 = first_x + algorithm_index * bar_width
                y1 = bottom - bar_height
                canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + bar_width - 3,
                    bottom,
                    fill=color,
                    outline="",
                )
                canvas.create_text(
                    x1 + (bar_width - 3) / 2,
                    y1 - 7,
                    text=f"{value:.2f}",
                    font=("Arial", 8),
                )
            canvas.create_text(
                center,
                bottom + 10,
                anchor="ne",
                angle=30,
                text=dataset,
                font=("Arial", 8),
            )

        canvas.configure(scrollregion=(0, 0, content_width, height))

    def _run_batch_analysis(self):
        input_path = self.batch_input_path.get().strip()
        output_path = self.batch_output_path.get().strip()
        if not input_path or not output_path:
            messagebox.showerror(
                "Batch Analysis",
                "Please select both the CSV folder and the output folder.",
            )
            return

        mode_map = {
            "Both": "both",
            "Non-Preemptive": "non-preemptive",
            "Preemptive": "preemptive",
        }
        try:
            aging_interval = self._aging_interval(
                self.batch_aging.get(),
                self.batch_interval.get(),
            )
            report = analyze_path(
                input_path,
                output_path,
                priority_mode=mode_map[self.batch_priority_mode.get()],
                aging_interval=aging_interval,
            )
        except (KeyError, OSError, TypeError, ValueError) as error:
            messagebox.showerror("Batch Analysis", str(error))
            return

        for item in self.batch_table.get_children():
            self.batch_table.delete(item)
        for row in report["statistics"]:
            status = row["status"]
            if status == "error":
                status = f"Error: {row['error']}"
            self.batch_table.insert(
                "",
                "end",
                values=(
                    row["dataset"],
                    row["algorithm"],
                    row["average_wt"],
                    row["average_tat"],
                    row["average_rt"],
                    row["context_switches"],
                    row["total_time"],
                    status,
                ),
            )

        self.batch_graph_rows = report["statistics"]
        self.update_idletasks()
        self._draw_batch_graph()

        self.batch_status.set(
            f"Processed {report['successful_files']}/{report['total_files']} files; "
            f"failed: {report['failed_files']}. Saved statistics.csv, summary.csv "
            f"and SVG graphs in {Path(output_path).resolve()}."
        )
        if report["failed_files"]:
            messagebox.showwarning(
                "Batch Analysis",
                "Analysis completed, but some CSV files were invalid. "
                "See the Status column and statistics.csv for details.",
            )
        else:
            messagebox.showinfo(
                "Batch Analysis",
                "Analysis completed and all statistics were saved.",
            )

    def _prepare_detail(self):
        try:
            processes = self._collect_processes()
            if self.detail_algorithm.get() == "FCFS":
                result = mo_phong_fcfs(processes)
            else:
                aging_interval = self._aging_interval(
                    self.detail_aging.get(),
                    self.detail_interval.get(),
                )
                if self.detail_mode.get() == "Preemptive":
                    result = mo_phong_priority_preemptive(processes, aging_interval)
                else:
                    result = mo_phong_priority_nonpreemptive(processes, aging_interval)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Không thể chuẩn bị", str(error))
            return

        self._stop_detail_playback()
        self.detail_result = result
        self.detail_index = 0
        self._render_detail()

    def _render_detail(self):
        if not self.detail_result or not self.detail_result["steps"]:
            return

        steps = self.detail_result["steps"]
        self.detail_index = max(0, min(self.detail_index, len(steps) - 1))
        step = steps[self.detail_index]

        self.detail_progress.set(f"Step {self.detail_index + 1}/{len(steps)}")
        self.detail_time.set(f"Time: {step['start']} → {step['end']}")
        self.detail_event.set(f"Event: {step['event']}")
        self.detail_cpu.set(f"CPU: {step['running']}")

        for item in self.detail_ready.get_children():
            self.detail_ready.delete(item)
        for process in step["ready"]:
            self.detail_ready.insert(
                "",
                "end",
                values=(
                    process["PID"],
                    process["remaining"],
                    process["priority"],
                    process["effective_priority"],
                ),
            )

        total_time = self.detail_result["gantt"][-1]["finish"]
        self.detail_gantt.draw(
            self.detail_result["gantt"],
            visible_until=step["end"],
            total_time=total_time,
        )
        self._set_text(self.detail_text, step["detail"])

        if self.detail_index == len(steps) - 1:
            self.detail_result_table.show(self.detail_result)
        else:
            self.detail_result_table.clear()

    def _detail_previous(self):
        self._stop_detail_playback()
        if self.detail_result and self.detail_index > 0:
            self.detail_index -= 1
            self._render_detail()

    def _detail_next(self):
        self._stop_detail_playback()
        if self.detail_result and self.detail_index < len(self.detail_result["steps"]) - 1:
            self.detail_index += 1
            self._render_detail()

    def _detail_toggle_play(self):
        if not self.detail_result:
            self._prepare_detail()
            if not self.detail_result:
                return
        if self.detail_after_id is not None:
            self._stop_detail_playback()
            return
        if self.detail_index >= len(self.detail_result["steps"]) - 1:
            self.detail_index = 0
            self._render_detail()
        self.detail_play_button.configure(text="Pause")
        self._schedule_detail_tick()

    def _schedule_detail_tick(self):
        delay = SPEED_DELAYS[self.detail_speed.get()]
        self.detail_after_id = self.after(delay, self._detail_tick)

    def _detail_tick(self):
        self.detail_after_id = None
        if not self.detail_result:
            return
        if self.detail_index >= len(self.detail_result["steps"]) - 1:
            self._stop_detail_playback()
            return
        self.detail_index += 1
        self._render_detail()
        if self.detail_index >= len(self.detail_result["steps"]) - 1:
            self._stop_detail_playback()
        else:
            self._schedule_detail_tick()

    def _stop_detail_playback(self):
        if self.detail_after_id is not None:
            self.after_cancel(self.detail_after_id)
            self.detail_after_id = None
        if hasattr(self, "detail_play_button"):
            self.detail_play_button.configure(text="Play")

    def _reset_detail(self):
        self._stop_detail_playback()
        self.detail_result = None
        self.detail_index = 0
        if not hasattr(self, "detail_gantt"):
            return
        self.detail_progress.set("Step 0/0")
        self.detail_time.set("Time: -")
        self.detail_event.set("Event: -")
        self.detail_cpu.set("CPU: -")
        for item in self.detail_ready.get_children():
            self.detail_ready.delete(item)
        self.detail_gantt.draw([])
        self.detail_result_table.clear()
        self._set_text(self.detail_text, "")

    def _prepare_comparison(self):
        try:
            processes = self._collect_processes()
            aging_interval = self._aging_interval(
                self.compare_aging.get(),
                self.compare_interval.get(),
            )
            fcfs = mo_phong_fcfs(processes)
            if self.compare_mode.get() == "Preemptive":
                priority = mo_phong_priority_preemptive(processes, aging_interval)
            else:
                priority = mo_phong_priority_nonpreemptive(processes, aging_interval)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Không thể so sánh", str(error))
            return

        self._stop_comparison_playback()
        self.comparison_results = {"FCFS": fcfs, "Priority": priority}
        self.comparison_total_time = max(
            fcfs["gantt"][-1]["finish"],
            priority["gantt"][-1]["finish"],
        )
        self.comparison_time = 0
        self._render_comparison()

    def _render_comparison(self):
        if not self.comparison_results:
            return

        fcfs = self.comparison_results["FCFS"]
        priority = self.comparison_results["Priority"]
        total = self.comparison_total_time
        current = max(0, min(self.comparison_time, total))
        self.comparison_time = current

        self.compare_time_label.set(f"Time: {current}/{total}")
        probe = current if current < total else max(0, total - 1)
        self.compare_fcfs_cpu.set(f"FCFS CPU: {_running_at(fcfs['gantt'], probe)}")
        self.compare_priority_cpu.set(
            f"Priority CPU: {_running_at(priority['gantt'], probe)}"
        )
        self.compare_fcfs_gantt.draw(fcfs["gantt"], current, total)
        self.compare_priority_gantt.draw(priority["gantt"], current, total)

        for item in self.compare_table.get_children():
            self.compare_table.delete(item)
        self.compare_analysis.configure(text="")

        if current >= total:
            for result in (fcfs, priority):
                self.compare_table.insert(
                    "",
                    "end",
                    values=(
                        result["algorithm"],
                        f"{result['average_waiting']:.2f}",
                        f"{result['average_turnaround']:.2f}",
                        f"{result['average_response']:.2f}",
                        result["context_switches"],
                    ),
                )
            self._show_comparison_analysis(fcfs, priority)

    def _show_comparison_analysis(self, fcfs, priority):
        if priority["average_waiting"] < fcfs["average_waiting"]:
            waiting_text = "Priority có WT trung bình thấp hơn FCFS."
        elif priority["average_waiting"] > fcfs["average_waiting"]:
            waiting_text = "FCFS có WT trung bình thấp hơn Priority."
        else:
            waiting_text = "FCFS và Priority có WT trung bình bằng nhau."

        if priority["context_switches"] < fcfs["context_switches"]:
            switch_text = "Priority có ít chuyển ngữ cảnh hơn."
        elif priority["context_switches"] > fcfs["context_switches"]:
            switch_text = "FCFS có ít chuyển ngữ cảnh hơn."
        else:
            switch_text = "Hai thuật toán có số chuyển ngữ cảnh bằng nhau."
        self.compare_analysis.configure(text=f"{waiting_text} {switch_text}")

    def _comparison_previous(self):
        self._stop_comparison_playback()
        if self.comparison_results and self.comparison_time > 0:
            self.comparison_time -= 1
            self._render_comparison()

    def _comparison_next(self):
        self._stop_comparison_playback()
        if self.comparison_results and self.comparison_time < self.comparison_total_time:
            self.comparison_time += 1
            self._render_comparison()

    def _comparison_toggle_play(self):
        if not self.comparison_results:
            self._prepare_comparison()
            if not self.comparison_results:
                return
        if self.comparison_after_id is not None:
            self._stop_comparison_playback()
            return
        if self.comparison_time >= self.comparison_total_time:
            self.comparison_time = 0
            self._render_comparison()
        self.compare_play_button.configure(text="Pause")
        self._schedule_comparison_tick()

    def _schedule_comparison_tick(self):
        delay = SPEED_DELAYS[self.compare_speed.get()]
        self.comparison_after_id = self.after(delay, self._comparison_tick)

    def _comparison_tick(self):
        self.comparison_after_id = None
        if not self.comparison_results:
            return
        if self.comparison_time >= self.comparison_total_time:
            self._stop_comparison_playback()
            return
        self.comparison_time += 1
        self._render_comparison()
        if self.comparison_time >= self.comparison_total_time:
            self._stop_comparison_playback()
        else:
            self._schedule_comparison_tick()

    def _stop_comparison_playback(self):
        if self.comparison_after_id is not None:
            self.after_cancel(self.comparison_after_id)
            self.comparison_after_id = None
        if hasattr(self, "compare_play_button"):
            self.compare_play_button.configure(text="Play")

    def _reset_comparison(self):
        self._stop_comparison_playback()
        self.comparison_results = None
        self.comparison_time = 0
        self.comparison_total_time = 0
        if not hasattr(self, "compare_fcfs_gantt"):
            return
        self.compare_time_label.set("Time: 0/0")
        self.compare_fcfs_cpu.set("FCFS CPU: -")
        self.compare_priority_cpu.set("Priority CPU: -")
        self.compare_fcfs_gantt.draw([])
        self.compare_priority_gantt.draw([])
        for item in self.compare_table.get_children():
            self.compare_table.delete(item)
        self.compare_analysis.configure(text="")

    @staticmethod
    def _set_text(widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _close(self):
        self._stop_detail_playback()
        self._stop_comparison_playback()
        self.destroy()


def main():
    app = SchedulingDemoV2()
    app.mainloop()


if __name__ == "__main__":
    main()
