from __future__ import annotations

import re
from typing import Iterable, Literal

from model import (
    AlgorithmComparison,
    GanttSegment,
    IDLE_PID,
    Process,
    ProcessMetrics,
    ReadySnapshot,
    ScheduleResult,
    SimulationRun,
    SimulationStep,
)
from service.module.module4_aging import tinh_priority_hieu_dung

AlgorithmKey = Literal[
    "fcfs",
    "sjf",
    "srtf",
    "priority_non_preemptive",
    "priority_preemptive",
    "round_robin",
]

ALGORITHM_LABELS: dict[AlgorithmKey, str] = {
    "fcfs": "FCFS",
    "sjf": "SJF (Non-Preemptive)",
    "srtf": "SRTF (Preemptive)",
    "priority_non_preemptive": "Priority Non-Preemptive",
    "priority_preemptive": "Priority Preemptive",
    "round_robin": "Round Robin",
}

LABEL_TO_KEY: dict[str, AlgorithmKey] = {label: key for key, label in ALGORITHM_LABELS.items()}


def _pid_key(pid: str) -> tuple[object, ...]:
    parts = re.split(r"(\d+)", pid.casefold())
    return tuple(int(part) if part.isdigit() else part for part in parts)


def _validate(processes: Iterable[Process]) -> tuple[Process, ...]:
    items = tuple(processes)
    if not items:
        raise ValueError("Cần ít nhất một process để mô phỏng.")
    seen: set[str] = set()
    for process in items:
        key = process.pid.casefold()
        if key in seen:
            raise ValueError(f"PID bị trùng: {process.pid}.")
        seen.add(key)
    return items


def _append_segment(segments: list[GanttSegment], pid: str, start: int, end: int) -> None:
    if end <= start:
        return
    if segments and segments[-1].pid == pid and segments[-1].end == start:
        previous = segments[-1]
        segments[-1] = GanttSegment(pid=pid, start=previous.start, end=end)
    else:
        segments.append(GanttSegment(pid=pid, start=start, end=end))


def _count_context_switches(segments: Iterable[GanttSegment]) -> int:
    active = [segment.pid for segment in segments if segment.pid != IDLE_PID]
    return sum(left != right for left, right in zip(active, active[1:]))


def _build_result(
    algorithm: str,
    processes: tuple[Process, ...],
    segments: list[GanttSegment],
    completion: dict[str, int],
    first_start: dict[str, int],
) -> ScheduleResult:
    metrics: list[ProcessMetrics] = []
    for process in sorted(processes, key=lambda item: _pid_key(item.pid)):
        ct = completion[process.pid]
        tat = ct - process.arrival
        wt = tat - process.burst
        rt = first_start[process.pid] - process.arrival
        metrics.append(
            ProcessMetrics(
                pid=process.pid,
                arrival=process.arrival,
                burst=process.burst,
                priority=process.priority,
                completion=ct,
                turnaround=tat,
                waiting=wt,
                response=rt,
            )
        )

    count = len(metrics)
    return ScheduleResult(
        algorithm=algorithm,
        segments=tuple(segments),
        metrics=tuple(metrics),
        average_waiting=sum(item.waiting for item in metrics) / count,
        average_turnaround=sum(item.turnaround for item in metrics) / count,
        average_response=sum(item.response for item in metrics) / count,
        context_switches=_count_context_switches(segments),
    )


def _effective_priority(
    process: Process,
    current_time: int,
    executed: int,
    aging_interval: int | None,
) -> int:
    return tinh_priority_hieu_dung(
        process,
        current_time=current_time,
        executed=executed,
        aging_interval=aging_interval,
    )


def _ready_snapshots(
    ready: Iterable[Process],
    remaining: dict[str, int],
    executed: dict[str, int],
    current_time: int,
    aging_interval: int | None,
    running: str | None,
    *,
    sort_key,
) -> tuple[ReadySnapshot, ...]:
    queued = [process for process in ready if process.pid != running and remaining[process.pid] > 0]
    queued.sort(key=sort_key)
    return tuple(
        ReadySnapshot(
            pid=process.pid,
            remaining=remaining[process.pid],
            priority=process.priority,
            effective_priority=_effective_priority(
                process,
                current_time,
                executed[process.pid],
                aging_interval,
            ),
        )
        for process in queued
    )


def _selection_key(
    algorithm: AlgorithmKey,
    process: Process,
    remaining: dict[str, int],
    executed: dict[str, int],
    current_time: int,
    aging_interval: int | None,
) -> tuple[object, ...]:
    if algorithm == "fcfs":
        return (process.arrival, _pid_key(process.pid))
    if algorithm == "sjf":
        return (process.burst, process.arrival, _pid_key(process.pid))
    if algorithm == "srtf":
        return (remaining[process.pid], process.arrival, _pid_key(process.pid))
    if algorithm in {"priority_non_preemptive", "priority_preemptive"}:
        return (
            _effective_priority(
                process,
                current_time,
                executed[process.pid],
                aging_interval,
            ),
            process.arrival,
            _pid_key(process.pid),
        )
    raise ValueError(f"Thuật toán không dùng selection key: {algorithm}")


def _describe_selection(
    algorithm: AlgorithmKey,
    process: Process,
    current_time: int,
    remaining: dict[str, int],
    executed: dict[str, int],
    aging_interval: int | None,
) -> str:
    if algorithm == "fcfs":
        return f"{process.pid} đến sớm nhất trong Ready Queue."
    if algorithm == "sjf":
        return f"{process.pid} có Burst Time nhỏ nhất ({process.burst})."
    if algorithm == "srtf":
        return f"{process.pid} có Remaining Time nhỏ nhất ({remaining[process.pid]})."
    effective = _effective_priority(
        process,
        current_time,
        executed[process.pid],
        aging_interval,
    )
    if aging_interval is None:
        return f"{process.pid} có Priority cao nhất (PR={effective}, số nhỏ hơn ưu tiên cao hơn)."
    return (
        f"{process.pid} có Effective Priority cao nhất (PR={effective}); "
        f"Aging Interval={aging_interval}."
    )


def _simulate_selection_algorithm(
    processes: tuple[Process, ...],
    algorithm: AlgorithmKey,
    aging_interval: int | None,
) -> SimulationRun:
    preemptive = algorithm in {"srtf", "priority_preemptive"}
    remaining = {process.pid: process.burst for process in processes}
    executed = {process.pid: 0 for process in processes}
    completion: dict[str, int] = {}
    first_start: dict[str, int] = {}
    segments: list[GanttSegment] = []
    steps: list[SimulationStep] = []
    current_time = 0
    running: Process | None = None

    while len(completion) < len(processes):
        ready = [
            process
            for process in processes
            if process.arrival <= current_time and remaining[process.pid] > 0
        ]
        arrivals = [process.pid for process in processes if process.arrival == current_time]

        if not ready:
            future = [
                process.arrival
                for process in processes
                if remaining[process.pid] > 0 and process.arrival > current_time
            ]
            next_arrival = min(future)
            _append_segment(segments, IDLE_PID, current_time, next_arrival)
            steps.append(
                SimulationStep(
                    start=current_time,
                    end=next_arrival,
                    running=IDLE_PID,
                    ready=(),
                    event="CPU IDLE",
                    detail=f"Không có process sẵn sàng. CPU chờ đến t={next_arrival}.",
                )
            )
            current_time = next_arrival
            running = None
            continue

        previous = running
        if running is None or remaining[running.pid] == 0:
            running = min(
                ready,
                key=lambda item: _selection_key(
                    algorithm,
                    item,
                    remaining,
                    executed,
                    current_time,
                    aging_interval,
                ),
            )
        elif preemptive:
            candidate = min(
                ready,
                key=lambda item: _selection_key(
                    algorithm,
                    item,
                    remaining,
                    executed,
                    current_time,
                    aging_interval,
                ),
            )
            running = candidate

        assert running is not None
        first_start.setdefault(running.pid, current_time)
        queue_sort_key = lambda item: _selection_key(
            algorithm,
            item,
            remaining,
            executed,
            current_time,
            aging_interval,
        )
        snapshots = _ready_snapshots(
            ready,
            remaining,
            executed,
            current_time,
            aging_interval,
            running.pid,
            sort_key=queue_sort_key,
        )

        if previous is not None and previous.pid != running.pid and remaining[previous.pid] > 0:
            event = "PREEMPTED"
            detail = (
                f"{previous.pid} bị tạm dừng. "
                + _describe_selection(
                    algorithm,
                    running,
                    current_time,
                    remaining,
                    executed,
                    aging_interval,
                )
            )
        elif running.pid not in first_start or first_start[running.pid] == current_time:
            event = "START"
            detail = _describe_selection(
                algorithm,
                running,
                current_time,
                remaining,
                executed,
                aging_interval,
            )
        elif arrivals:
            event = "NEW ARRIVAL / EXEC"
            joined = ", ".join(arrivals)
            detail = f"Process mới đến: {joined}. {running.pid} tiếp tục chạy."
        else:
            event = "EXEC"
            detail = f"{running.pid} tiếp tục thực thi; remaining={remaining[running.pid]}."

        _append_segment(segments, running.pid, current_time, current_time + 1)
        steps.append(
            SimulationStep(
                start=current_time,
                end=current_time + 1,
                running=running.pid,
                ready=snapshots,
                event=event,
                detail=detail,
            )
        )
        remaining[running.pid] -= 1
        executed[running.pid] += 1
        current_time += 1

        if remaining[running.pid] == 0:
            completion[running.pid] = current_time
            if steps:
                last = steps[-1]
                steps[-1] = SimulationStep(
                    start=last.start,
                    end=last.end,
                    running=last.running,
                    ready=last.ready,
                    event="FINISHED" if last.event == "EXEC" else f"{last.event} / FINISHED",
                    detail=f"{last.detail} {running.pid} hoàn thành tại t={current_time}.",
                )
            running = None

    label = ALGORITHM_LABELS[algorithm]
    if algorithm in {"priority_non_preemptive", "priority_preemptive"} and aging_interval is not None:
        label += " + Aging"
    return SimulationRun(
        result=_build_result(label, processes, segments, completion, first_start),
        steps=tuple(steps),
    )


def _simulate_round_robin(processes: tuple[Process, ...], quantum: int) -> SimulationRun:
    if quantum <= 0:
        raise ValueError("Time Quantum phải > 0.")

    ordered = sorted(processes, key=lambda item: (item.arrival, _pid_key(item.pid)))
    by_pid = {process.pid: process for process in processes}
    remaining = {process.pid: process.burst for process in processes}
    first_start: dict[str, int] = {}
    completion: dict[str, int] = {}
    segments: list[GanttSegment] = []
    steps: list[SimulationStep] = []
    ready_queue: list[str] = []
    current_time = 0
    next_arrival_index = 0

    def enqueue_arrivals(up_to_time: int) -> list[str]:
        nonlocal next_arrival_index
        added: list[str] = []
        while next_arrival_index < len(ordered) and ordered[next_arrival_index].arrival <= up_to_time:
            pid = ordered[next_arrival_index].pid
            if remaining[pid] > 0 and pid not in ready_queue:
                ready_queue.append(pid)
                added.append(pid)
            next_arrival_index += 1
        return added

    while len(completion) < len(processes):
        arrivals = enqueue_arrivals(current_time)
        if not ready_queue:
            next_time = ordered[next_arrival_index].arrival
            _append_segment(segments, IDLE_PID, current_time, next_time)
            steps.append(
                SimulationStep(
                    start=current_time,
                    end=next_time,
                    running=IDLE_PID,
                    ready=(),
                    event="CPU IDLE",
                    detail=f"Ready Queue rỗng. CPU chờ đến t={next_time}.",
                )
            )
            current_time = next_time
            continue

        pid = ready_queue.pop(0)
        process = by_pid[pid]
        first_start.setdefault(pid, current_time)
        slice_time = min(quantum, remaining[pid])

        for offset in range(slice_time):
            tick_start = current_time
            new_arrivals = arrivals if offset == 0 else enqueue_arrivals(current_time)
            snapshots = tuple(
                ReadySnapshot(
                    pid=queued_pid,
                    remaining=remaining[queued_pid],
                    priority=by_pid[queued_pid].priority,
                    effective_priority=by_pid[queued_pid].priority,
                )
                for queued_pid in ready_queue
            )
            event = "TIME SLICE START" if offset == 0 else "EXEC"
            detail = f"{pid} chạy với quantum={quantum}; remaining trước tick={remaining[pid]}."
            if new_arrivals:
                detail += f" Process mới đến: {', '.join(new_arrivals)}."

            _append_segment(segments, pid, tick_start, tick_start + 1)
            steps.append(
                SimulationStep(
                    start=tick_start,
                    end=tick_start + 1,
                    running=pid,
                    ready=snapshots,
                    event=event,
                    detail=detail,
                )
            )
            remaining[pid] -= 1
            current_time += 1
            enqueue_arrivals(current_time)
            if remaining[pid] == 0:
                completion[pid] = current_time
                last = steps[-1]
                steps[-1] = SimulationStep(
                    start=last.start,
                    end=last.end,
                    running=last.running,
                    ready=last.ready,
                    event=f"{last.event} / FINISHED",
                    detail=f"{last.detail} {pid} hoàn thành tại t={current_time}.",
                )
                break

        if remaining[pid] > 0:
            ready_queue.append(pid)
            last = steps[-1]
            steps[-1] = SimulationStep(
                start=last.start,
                end=last.end,
                running=last.running,
                ready=last.ready,
                event="QUANTUM EXPIRED",
                detail=f"{last.detail} Hết quantum, {pid} quay lại cuối Ready Queue.",
            )

    return SimulationRun(
        result=_build_result(
            f"Round Robin (q={quantum})",
            processes,
            segments,
            completion,
            first_start,
        ),
        steps=tuple(steps),
    )


def simulate_algorithm(
    processes: Iterable[Process],
    algorithm: AlgorithmKey,
    *,
    aging_interval: int | None = None,
    quantum: int = 2,
) -> SimulationRun:
    items = _validate(processes)
    if aging_interval is not None and aging_interval <= 0:
        raise ValueError("Aging Interval phải > 0.")
    if algorithm == "round_robin":
        return _simulate_round_robin(items, quantum)
    if algorithm not in ALGORITHM_LABELS:
        raise ValueError(f"Thuật toán không được hỗ trợ: {algorithm}")
    return _simulate_selection_algorithm(items, algorithm, aging_interval)


def build_comparison(
    processes: Iterable[Process],
    *,
    priority_preemptive: bool = True,
    aging_interval: int | None = None,
    quantum: int = 2,
) -> tuple[AlgorithmComparison, ...]:
    items = _validate(processes)
    priority_key: AlgorithmKey = (
        "priority_preemptive" if priority_preemptive else "priority_non_preemptive"
    )
    requested: tuple[AlgorithmKey, ...] = (
        "fcfs",
        "sjf",
        "srtf",
        priority_key,
        "round_robin",
    )
    comparisons: list[AlgorithmComparison] = []
    for key in requested:
        run = simulate_algorithm(
            items,
            key,
            aging_interval=aging_interval if key.startswith("priority") else None,
            quantum=quantum,
        )
        comparisons.append(AlgorithmComparison(name=run.result.algorithm, result=run.result))
    return tuple(comparisons)
