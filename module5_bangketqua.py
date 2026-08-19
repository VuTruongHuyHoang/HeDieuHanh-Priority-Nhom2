import tkinter as tk
from collections.abc import Mapping
from tkinter import ttk


COLUMNS = ("PID", "AT", "BT", "PR", "CT", "TAT", "WT", "RT")


def build_result_rows(result):
    """Lấy dữ liệu tiến trình để hiển thị mà không sửa kết quả gốc."""
    if not isinstance(result, Mapping):
        raise TypeError("Kết quả mô phỏng phải là dictionary.")

    processes = result.get("processes", [])
    if not isinstance(processes, (list, tuple)):
        raise TypeError("Trường processes phải là list hoặc tuple.")

    rows = []
    for process in processes:
        if not isinstance(process, Mapping):
            raise TypeError("Mỗi tiến trình trong kết quả phải là dictionary.")
        if not str(process.get("PID", "")).strip():
            raise ValueError("Mỗi tiến trình phải có PID.")

        rows.append({column: process.get(column, "") for column in COLUMNS})

    return rows


def _average_from_rows(rows, column):
    values = [row[column] for row in rows if isinstance(row[column], (int, float))]
    return sum(values) / len(values) if values else 0.0


def build_result_summary(result):
    """Tạo dòng tổng kết ngắn dùng cho giao diện."""
    rows = build_result_rows(result)
    algorithm = str(result.get("algorithm", "Chưa xác định"))
    average_waiting = result.get("average_waiting", _average_from_rows(rows, "WT"))
    average_turnaround = result.get("average_turnaround", _average_from_rows(rows, "TAT"))
    average_response = result.get("average_response", _average_from_rows(rows, "RT"))
    context_switches = result.get("context_switches", 0)

    return (
        f"{algorithm} | WT TB={float(average_waiting):.2f} | "
        f"TAT TB={float(average_turnaround):.2f} | "
        f"RT TB={float(average_response):.2f} | "
        f"Chuyển ngữ cảnh={context_switches}"
    )


def build_result_view_data(result):
    """Trả dữ liệu trung lập để Main UI có thể tự hiển thị nếu cần."""
    return {
        "algorithm": str(result.get("algorithm", "Chưa xác định")),
        "summary": build_result_summary(result),
        "rows": build_result_rows(result),
    }


class ResultTable(ttk.Frame):
    """Bảng Tkinter hiển thị metrics của một kết quả mô phỏng."""

    def __init__(self, parent):
        super().__init__(parent, padding=8)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.summary_label = ttk.Label(
            self,
            text="Chưa có kết quả",
            anchor="center",
        )
        self.summary_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            height=8,
        )
        for column in COLUMNS:
            self.table.heading(column, text=column)
            self.table.column(column, width=75, anchor="center", stretch=True)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def clear(self):
        self.summary_label.configure(text="Chưa có kết quả")
        for item in self.table.get_children():
            self.table.delete(item)

    def show(self, result):
        data = build_result_view_data(result)
        self.clear()
        self.summary_label.configure(text=data["summary"])

        for row in data["rows"]:
            self.table.insert(
                "",
                "end",
                values=tuple(row[column] for column in COLUMNS),
            )


ResultPanel = ResultTable


def render_result_panel(parent, result):
    panel = ResultTable(parent)
    panel.show(result)
    return panel


if __name__ == "__main__":
    demo_result = {
        "algorithm": "FCFS",
        "processes": [
            {
                "PID": "P1",
                "AT": 0,
                "BT": 5,
                "PR": 2,
                "CT": 5,
                "TAT": 5,
                "WT": 0,
                "RT": 0,
            }
        ],
        "average_waiting": 0.0,
        "average_turnaround": 5.0,
        "average_response": 0.0,
        "context_switches": 0,
    }

    root = tk.Tk()
    root.title("Module 5 - Bảng kết quả")
    result_table = ResultTable(root)
    result_table.pack(fill="both", expand=True)
    result_table.show(demo_result)
    root.mainloop()
