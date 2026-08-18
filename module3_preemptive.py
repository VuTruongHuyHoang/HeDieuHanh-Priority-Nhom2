def priority_preemptive(processes):
    n = len(processes)
    remaining = [p["burst"] for p in processes]
    completion = [0] * n
    current_time = 0
    completed = 0
    gantt = []
    while completed < n:
        selected = -1
        for i in range(n):
            if processes[i]["arrival"] <= current_time and remaining[i] > 0:
                if selected == -1:
                    selected = i
                elif processes[i]["priority"] < processes[selected]["priority"]:
                    selected = i
                elif processes[i]["priority"] == processes[selected]["priority"] \
                        and processes[i]["arrival"] < processes[selected]["arrival"]:
                    selected = i
        if selected == -1:
            current_time += 1
            continue
        remaining[selected] -= 1
        current_time += 1
        if not gantt or gantt[-1] != processes[selected]["pid"]:
            gantt.append(processes[selected]["pid"])
        if remaining[selected] == 0:
            completion[selected] = current_time
            completed += 1
    turnaround = [completion[i] - processes[i]["arrival"] for i in range(n)]
    waiting = [turnaround[i] - processes[i]["burst"] for i in range(n)]

    return completion, turnaround, waiting, gantt
