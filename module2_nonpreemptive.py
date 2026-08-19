from module1_nhaplieu import chuan_hoa_danh_sach
from module4_aging import tinh_priority_hieu_dung


def _context_switches(gantt):
    pids = [item["pid"] for item in gantt if item["pid"] != "Idle"]
    return sum(pids[index] != pids[index - 1] for index in range(1, len(pids)))


def _ready_snapshot(processes, completed, running_pid, current_time, aging_interval):
    ready = []
    for process in processes:
        pid = process["PID"]
        if process["AT"] > current_time or pid in completed or pid == running_pid:
            continue
        ready.append({
            "PID": pid,
            "remaining": process["BT"],
            "priority": process["PR"],
            "effective_priority": tinh_priority_hieu_dung(
                process,
                current_time,
                aging_interval=aging_interval,
            ),
        })
    return ready


def mo_phong_priority_nonpreemptive(processes, aging_interval=None):
    """Mô phỏng Priority Non-Preemptive và trả dữ liệu dùng chung cho UI."""
    processes = chuan_hoa_danh_sach(processes)
    pending = sorted(
        enumerate(processes),
        key=lambda item: (item[1]["AT"], item[0]),
    )
    ready_queue = []
    completed = {}
    gantt = []
    steps = []
    current_time = 0

    while pending or ready_queue:
        while pending and pending[0][1]["AT"] <= current_time:
            ready_queue.append(pending.pop(0))

        if not ready_queue:
            next_time = pending[0][1]["AT"]
            gantt.append({"pid": "Idle", "start": current_time, "finish": next_time})
            steps.append({
                "start": current_time,
                "end": next_time,
                "running": "Idle",
                "ready": [],
                "event": "CPU IDLE",
                "detail": f"CPU chờ tiến trình tiếp theo đến t={next_time}.",
            })
            current_time = next_time
            continue

        index, selected = min(
            ready_queue,
            key=lambda item: (
                tinh_priority_hieu_dung(
                    item[1],
                    current_time,
                    aging_interval=aging_interval,
                ),
                item[1]["AT"],
                item[0],
            ),
        )
        ready_queue.remove((index, selected))

        start_time = current_time
        finish_time = start_time + selected["BT"]
        current_time = finish_time

        gantt.append({"pid": selected["PID"], "start": start_time, "finish": finish_time})
        for tick in range(start_time, finish_time):
            event = "EXEC / FINISHED" if tick == finish_time - 1 else "EXEC"
            detail = f"{selected['PID']} chạy từ t={tick} đến t={tick + 1}."
            if tick == finish_time - 1:
                detail += f" {selected['PID']} hoàn thành tại t={tick + 1}."
            steps.append({
                "start": tick,
                "end": tick + 1,
                "running": selected["PID"],
                "ready": _ready_snapshot(
                    processes,
                    completed,
                    selected["PID"],
                    tick,
                    aging_interval,
                ),
                "event": event,
                "detail": detail,
            })

        turnaround = finish_time - selected["AT"]
        waiting = turnaround - selected["BT"]
        completed[selected["PID"]] = {
            **selected,
            "CT": finish_time,
            "TAT": turnaround,
            "WT": waiting,
            "RT": start_time - selected["AT"],
        }

    result_processes = [completed[process["PID"]] for process in processes]
    count = len(result_processes)
    suffix = " + Aging" if aging_interval is not None else ""

    return {
        "algorithm": f"Priority Non-Preemptive{suffix}",
        "processes": result_processes,
        "gantt": gantt,
        "steps": steps,
        "average_waiting": sum(p["WT"] for p in result_processes) / count,
        "average_turnaround": sum(p["TAT"] for p in result_processes) / count,
        "average_response": sum(p["RT"] for p in result_processes) / count,
        "context_switches": _context_switches(gantt),
    }


def priority_non_preemptive(processes):
    """API cũ: chỉ trả thứ tự các tiến trình đã chạy."""
    result = mo_phong_priority_nonpreemptive(processes)
    return [item["pid"] for item in result["gantt"] if item["pid"] != "Idle"]


def chay_thuattoan_nonpreemptive(processes, aging_interval=None):
    return mo_phong_priority_nonpreemptive(processes, aging_interval)
