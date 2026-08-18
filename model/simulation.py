from __future__ import annotations

from dataclasses import dataclass

from .result import ScheduleResult


@dataclass(frozen=True, slots=True)
class ReadySnapshot:
    pid: str
    remaining: int
    priority: int
    effective_priority: int


@dataclass(frozen=True, slots=True)
class SimulationStep:
    start: int
    end: int
    running: str
    ready: tuple[ReadySnapshot, ...]
    event: str
    detail: str


@dataclass(frozen=True, slots=True)
class SimulationRun:
    result: ScheduleResult
    steps: tuple[SimulationStep, ...]


@dataclass(frozen=True, slots=True)
class AlgorithmComparison:
    name: str
    result: ScheduleResult
