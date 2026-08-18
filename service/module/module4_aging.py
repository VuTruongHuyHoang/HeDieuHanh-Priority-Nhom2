from __future__ import annotations

from model import Process


def tinh_priority_hieu_dung(
    process: Process,
    *,
    current_time: int,
    executed: int = 0,
    aging_interval: int | None = None,
) -> int:
    if aging_interval is None:
        return process.priority
    if aging_interval <= 0:
        raise ValueError("Aging Interval phải > 0.")
    waited = max(0, current_time - process.arrival - executed)
    return max(1, process.priority - waited // aging_interval)
