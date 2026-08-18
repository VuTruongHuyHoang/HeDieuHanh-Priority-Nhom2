from __future__ import annotations

from collections.abc import Iterable

from model import Process, ScheduleResult, SimulationRun
from service.misc.scheduling import simulate_algorithm


def mo_phong_priority_preemptive(
    processes: Iterable[Process], *, aging_interval: int | None = None
) -> SimulationRun:
    return simulate_algorithm(
        processes,
        "priority_preemptive",
        aging_interval=aging_interval,
    )


def chay_thuattoan_preemptive(
    processes: Iterable[Process], *, aging_interval: int | None = None
) -> ScheduleResult:
    return mo_phong_priority_preemptive(
        processes,
        aging_interval=aging_interval,
    ).result
