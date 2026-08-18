from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TypedDict

from model import ScheduleResult
from service.module.module6_ganttchart import TimelineGanttCanvas


class MetricViewData(TypedDict):
    pid: str
    arrival: int
    burst: int
    priority: int
    completion: int
    turnaround: int
    waiting: int
    response: int


class ResultViewData(TypedDict):
    algorithm: str
    summary: str
    metrics: list[MetricViewData]


def build_result_view_data(result: ScheduleResult) -> ResultViewData:
    """Return UI-neutral data for module8_mainui to render itself."""
    return {
        "algorithm": result.algorithm,
        "summary": (
            f"{result.algorithm} | Avg WT={result.average_waiting:.2f} | "
            f"Avg TAT={result.average_turnaround:.2f} | "
            f"Avg RT={result.average_response:.2f} | "
            f"Context Switch={result.context_switches}"
        ),
        "metrics": [
            {
                "pid": metric.pid,
                "arrival": metric.arrival,
                "burst": metric.burst,
                "priority": metric.priority,
                "completion": metric.completion,
                "turnaround": metric.turnaround,
                "waiting": metric.waiting,
                "response": metric.response,
            }
            for metric in result.metrics
        ],
    }


class ResultPanel(ttk.Frame):
    """Alternative self-rendering result component for standalone reuse."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=8)
        self.columnconfigure(0, weight=1)
        self.summary = ttk.Label(self, text="Chưa có kết quả", anchor="center")
        self.summary.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.gantt = TimelineGanttCanvas(self)
        self.gantt.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        columns = ("pid", "at", "bt", "pr", "ct", "tat", "wt", "rt")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for column, heading in zip(columns, ("PID", "AT", "BT", "PR", "CT", "TAT", "WT", "RT")):
            self.table.heading(column, text=heading)
            self.table.column(column, width=78, anchor="center", stretch=True)
        self.table.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)

    def show(self, result: ScheduleResult) -> None:
        data = build_result_view_data(result)
        self.summary.configure(text=data["summary"])
        self.gantt.show(result)
        for item in self.table.get_children():
            self.table.delete(item)
        for metric in data["metrics"]:
            self.table.insert("", "end", values=tuple(metric.values()))


def render_result_panel(master: tk.Misc, result: ScheduleResult) -> ResultPanel:
    panel = ResultPanel(master)
    panel.show(result)
    return panel
