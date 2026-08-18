from __future__ import annotations

from collections.abc import Iterable, Mapping

from model import Process


def tao_tien_trinh(pid: str, arrival: str | int, burst: str | int, priority: str | int) -> Process:
    """Parse one UI/input row into the shared validated Process model."""
    try:
        return Process(pid, int(arrival), int(burst), int(priority))
    except (TypeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith(("PID", "Arrival", "Burst", "Priority")):
            raise
        raise ValueError("AT, BT và Priority phải là số nguyên.") from error


def tu_mapping(row: Mapping[str, object]) -> Process:
    normalized = {str(key).casefold(): value for key, value in row.items()}

    def value(*names: str) -> object:
        for name in names:
            if name.casefold() in normalized:
                return normalized[name.casefold()]
        raise KeyError(names[0])

    try:
        return tao_tien_trinh(
            str(value("PID")),
            value("AT", "arrival"),
            value("BT", "burst"),
            value("PR", "priority"),
        )
    except KeyError as error:
        raise ValueError(f"Thiếu trường tiến trình: {error.args[0]}") from error


def chuan_hoa_danh_sach(
    rows: Iterable[Process | Mapping[str, object]],
) -> tuple[Process, ...]:
    processes = tuple(row if isinstance(row, Process) else tu_mapping(row) for row in rows)
    if not processes:
        raise ValueError("Cần ít nhất một process để mô phỏng.")
    seen: set[str] = set()
    for process in processes:
        key = process.pid.casefold()
        if key in seen:
            raise ValueError(f"PID bị trùng: {process.pid}.")
        seen.add(key)
    return processes
