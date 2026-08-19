from module1_nhaplieu import chuan_hoa_danh_sach
from module4_aging import tinh_priority_hieu_dung


def _append_segment(gantt, pid, start, finish):
    if gantt and gantt[-1]["pid"] == pid and gantt[-1]["finish"] == start:
        gantt[-1]["finish"] = finish
    else:
        gantt.append({"pid": pid, "start": start, "finish": finish})


def _context_switches(gantt):
    pids = [item["pid"] for item in gantt if item["pid"] != "Idle"]
    return sum(pids[index] != pids[index - 1] for index in range(1, len(pids)))


def _ready_snapshot(processes, remaining, selected, current_time, aging_interval):
    ready = []
    for index, process in enumerate(processes):
        if index == selected or process["AT"] > current_time or remaining[index] <= 0:
            continue
        ready.append({
            "PID": process["PID"],
            "remaining": remaining[index],
            "priority": process["PR"],
            "effective_priority": tinh_priority_hieu_dung(
                process,
                current_time,
                executed=process["BT"] - remaining[index],
                aging_interval=aging_interval,
            ),
        })
    return ready


def mo_phong_priority_preemptive(processes, aging_interval=None):
    """Mô phỏng Priority Preemptive theo từng đơn vị thời gian."""
    processes = chuan_hoa_danh_sach(processes)
    count = len(processes)
    remaining = [process["BT"] for process in processes]
    completion = [0] * count
    first_start = [None] * count
    completed = 0
    current_time = 0
    running_index = None
    gantt = []
    steps = []

    while completed < count:
        ready = [
            index
            for index, process in enumerate(processes)
            if process["AT"] <= current_time and remaining[index] > 0
        ]

        if not ready:
            _append_segment(gantt, "Idle", current_time, current_time + 1)
            steps.append({
                "start": current_time,
                "end": current_time + 1,
                "running": "Idle",
                "ready": [],
                "event": "CPU IDLE",
                "detail": f"CPU không có tiến trình tại t={current_time}.",
            })
            current_time += 1
            running_index = None
            continue

        selected = min(
            ready,
            key=lambda index: (
                tinh_priority_hieu_dung(
                    processes[index],
                    current_time,
                    executed=processes[index]["BT"] - remaining[index],
                    aging_interval=aging_interval,
                ),
                processes[index]["AT"],
                index,
            ),
        )

        previous_index = running_index
        event = "EXEC"
        if running_index is not None and running_index != selected:
            event = "PREEMPTED"

        if first_start[selected] is None:
            first_start[selected] = current_time

        selected_pid = processes[selected]["PID"]
        _append_segment(gantt, selected_pid, current_time, current_time + 1)
        detail = f"{selected_pid} chạy từ t={current_time} đến t={current_time + 1}."
        if event == "PREEMPTED":
            previous_pid = processes[previous_index]["PID"]
            detail = f"{selected_pid} preempt {previous_pid} tại t={current_time}. " + detail

        step = {
            "start": current_time,
            "end": current_time + 1,
            "running": selected_pid,
            "ready": _ready_snapshot(
                processes,
                remaining,
                selected,
                current_time,
                aging_interval,
            ),
            "event": event,
            "detail": detail,
        }

        remaining[selected] -= 1
        current_time += 1
        running_index = selected

        if remaining[selected] == 0:
            completion[selected] = current_time
            completed += 1
            running_index = None
            step["event"] += " / FINISHED"
            step["detail"] += f" {selected_pid} hoàn thành tại t={current_time}."

        steps.append(step)

    result_processes = []
    for index, process in enumerate(processes):
        turnaround = completion[index] - process["AT"]
        waiting = turnaround - process["BT"]
        result_processes.append({
            **process,
            "CT": completion[index],
            "TAT": turnaround,
            "WT": waiting,
            "RT": first_start[index] - process["AT"],
        })

    suffix = " + Aging" if aging_interval is not None else ""
    return {
        "algorithm": f"Priority Preemptive{suffix}",
        "processes": result_processes,
        "gantt": gantt,
        "steps": steps,
        "average_waiting": sum(p["WT"] for p in result_processes) / count,
        "average_turnaround": sum(p["TAT"] for p in result_processes) / count,
        "average_response": sum(p["RT"] for p in result_processes) / count,
        "context_switches": _context_switches(gantt),
    }


def priority_preemptive(processes):
    """API cũ: trả các mảng metrics và thứ tự Gantt như trước."""
    result = mo_phong_priority_preemptive(processes)
    rows = result["processes"]
    gantt = [item["pid"] for item in result["gantt"] if item["pid"] != "Idle"]
    return (
        [row["CT"] for row in rows],
        [row["TAT"] for row in rows],
        [row["WT"] for row in rows],
        gantt,
    )


def chay_thuattoan_preemptive(processes, aging_interval=None):
    return mo_phong_priority_preemptive(processes, aging_interval)
