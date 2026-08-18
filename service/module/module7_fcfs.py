from __future__ import annotations

from collections.abc import Iterable, Mapping

from model import Process, ScheduleResult, SimulationRun
from service.misc.scheduling import simulate_algorithm
from service.module.module1_nhaplieu import chuan_hoa_danh_sach


def mo_phong_fcfs(processes: Iterable[Process]) -> SimulationRun:
    return simulate_algorithm(processes, "fcfs")


def schedule_fcfs(processes: Iterable[Process]) -> ScheduleResult:
    return mo_phong_fcfs(processes).result


def chay_thuattoan_fcfs(
    danh_sach_tien_trinh: Iterable[Mapping[str, object]],
) -> tuple[list[dict[str, object]], float, float]:
    """Compatibility API retained for the original dictionary-based module."""
    result = schedule_fcfs(chuan_hoa_danh_sach(danh_sach_tien_trinh))
    rows = [
        {
            "PID": metric.pid,
            "AT": metric.arrival,
            "BT": metric.burst,
            "PR": metric.priority,
            "CT": metric.completion,
            "TAT": metric.turnaround,
            "WT": metric.waiting,
            "RT": metric.response,
        }
        for metric in result.metrics
    ]
    return rows, round(result.average_waiting, 2), round(result.average_turnaround, 2)
