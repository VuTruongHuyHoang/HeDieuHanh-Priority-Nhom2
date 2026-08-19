from module1_nhaplieu import chuan_hoa_danh_sach


def _ready_snapshot(processes, completed, running_pid, current_time):
    ready = []
    for process in processes:
        pid = process["PID"]
        if process["AT"] > current_time or pid in completed or pid == running_pid:
            continue
        ready.append({
            "PID": pid,
            "remaining": process["BT"],
            "priority": process["PR"],
            "effective_priority": process["PR"],
        })
    return ready


def mo_phong_fcfs(danh_sach_tien_trinh):
    processes = chuan_hoa_danh_sach(danh_sach_tien_trinh)
    indexed = list(enumerate(processes))
    sorted_processes = sorted(indexed, key=lambda item: (item[1]["AT"], item[0]))

    current_time = 0
    gantt = []
    steps = []
    completed = {}

    for _, process in sorted_processes:
        if current_time < process["AT"]:
            gantt.append({"pid": "Idle", "start": current_time, "finish": process["AT"]})
            steps.append({
                "start": current_time,
                "end": process["AT"],
                "running": "Idle",
                "ready": [],
                "event": "CPU IDLE",
                "detail": f"CPU chờ tiến trình tiếp theo đến t={process['AT']}.",
            })
            current_time = process["AT"]

        start_time = current_time
        completion_time = start_time + process["BT"]
        turnaround = completion_time - process["AT"]
        waiting = turnaround - process["BT"]

        gantt.append({
            "pid": process["PID"],
            "start": start_time,
            "finish": completion_time,
        })
        for tick in range(start_time, completion_time):
            event = "EXEC / FINISHED" if tick == completion_time - 1 else "EXEC"
            detail = f"{process['PID']} chạy từ t={tick} đến t={tick + 1}."
            if tick == completion_time - 1:
                detail += f" {process['PID']} hoàn thành tại t={tick + 1}."
            steps.append({
                "start": tick,
                "end": tick + 1,
                "running": process["PID"],
                "ready": _ready_snapshot(
                    processes,
                    completed,
                    process["PID"],
                    tick,
                ),
                "event": event,
                "detail": detail,
            })
        completed[process["PID"]] = {
            **process,
            "CT": completion_time,
            "TAT": turnaround,
            "WT": waiting,
            "RT": start_time - process["AT"],
        }
        current_time = completion_time

    result_processes = [completed[process["PID"]] for process in processes]
    count = len(result_processes)
    real_segments = [item for item in gantt if item["pid"] != "Idle"]

    return {
        "algorithm": "FCFS",
        "processes": result_processes,
        "gantt": gantt,
        "steps": steps,
        "average_waiting": sum(p["WT"] for p in result_processes) / count,
        "average_turnaround": sum(p["TAT"] for p in result_processes) / count,
        "average_response": sum(p["RT"] for p in result_processes) / count,
        "context_switches": max(0, len(real_segments) - 1),
    }


def chay_thuattoan_fcfs(danh_sach_tien_trinh):
    """API cũ: trả bảng kết quả cùng WT và TAT trung bình."""
    result = mo_phong_fcfs(danh_sach_tien_trinh)
    return (
        result["processes"],
        round(result["average_waiting"], 2),
        round(result["average_turnaround"], 2),
    )


if __name__ == "__main__":
    import dummy_data

    rows, average_waiting, average_turnaround = chay_thuattoan_fcfs(
        dummy_data.danh_sach_test
    )
    print("=== THUẬT TOÁN FCFS (MODULE 7) ===")
    print(f"{'PID':<5} | {'CT':<5} | {'TAT':<5} | {'WT':<5} | {'RT':<5}")
    print("-" * 43)
    for process in rows:
        print(
            f"{process['PID']:<5} | {process['CT']:<5} | "
            f"{process['TAT']:<5} | {process['WT']:<5} | {process['RT']:<5}"
        )
    print(f"WT trung bình: {average_waiting}")
    print(f"TAT trung bình: {average_turnaround}")
