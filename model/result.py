from __future__ import annotations

from dataclasses import dataclass

IDLE_PID = "Idle"


@dataclass(frozen=True, slots=True)
class GanttSegment:
    pid: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class ProcessMetrics:
    pid: str
    arrival: int
    burst: int
    priority: int
    completion: int
    turnaround: int
    waiting: int
    response: int


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    algorithm: str
    segments: tuple[GanttSegment, ...]
    metrics: tuple[ProcessMetrics, ...]
    average_waiting: float
    average_turnaround: float
    average_response: float
    context_switches: int


@dataclass(frozen=True, slots=True)
class ComparisonRow:
    metric: str
    priority_value: float
    fcfs_value: float
    delta: float
    improvement_percent: float | None
    verdict: str
