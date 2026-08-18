from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int

    def __post_init__(self) -> None:
        clean_pid = self.pid.strip()
        if not clean_pid:
            raise ValueError("PID không được để trống.")
        if self.arrival < 0:
            raise ValueError(f"Arrival Time của {clean_pid} phải >= 0.")
        if self.burst <= 0:
            raise ValueError(f"Burst Time của {clean_pid} phải > 0.")
        if self.priority <= 0:
            raise ValueError(f"Priority của {clean_pid} phải > 0.")
        object.__setattr__(self, "pid", clean_pid)
