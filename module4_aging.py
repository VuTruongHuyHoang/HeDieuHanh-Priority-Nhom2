from dataclasses import dataclass, field
from typing import List, Optional
import copy


def tinh_priority_hieu_dung(
    process,
    current_time,
    executed=0,
    aging_interval=None,
):
    """Tính Priority sau Aging mà không thay đổi tiến trình gốc."""
    if isinstance(process, dict):
        priority = process["PR"]
        arrival_time = process["AT"]
    else:
        priority = getattr(process, "original_priority", process.priority)
        arrival_time = process.arrival_time

    if aging_interval is None:
        return priority
    if aging_interval <= 0:
        raise ValueError("Aging interval phải lớn hơn 0.")

    waiting_time = max(0, current_time - arrival_time - executed)
    return max(0, priority - waiting_time // aging_interval)


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int

    original_priority: int = field(init=False)
    remaining_time: int = field(init=False)
    start_time: Optional[int] = field(default=None, init=False)
    completion_time: Optional[int] = field(default=None, init=False)
    waiting_time: int = field(default=0, init=False)
    turnaround_time: int = field(default=0, init=False)

    def __post_init__(self):
        self.original_priority = self.priority
        self.remaining_time = self.burst_time


class AgingPriorityScheduler:
    def __init__(self, processes: List[Process], aging_interval=3, aging_factor=1,
                 min_priority=0, enable_aging=True):
        self.processes = copy.deepcopy(processes)
        self.aging_interval = aging_interval
        self.aging_factor = aging_factor
        self.min_priority = min_priority
        self.enable_aging = enable_aging

        if self.enable_aging and self.aging_interval <= 0:
            raise ValueError("Aging interval phải lớn hơn 0.")

        self.gantt_chart = []
        self.aging_log = []

    def _apply_aging(self, ready_queue, current_time):
        if not self.enable_aging:
            return

        for p in ready_queue:
            effective_priority = tinh_priority_hieu_dung(
                p,
                current_time,
                aging_interval=self.aging_interval,
            )
            improvement = (p.original_priority - effective_priority) * self.aging_factor
            new_priority = max(self.min_priority, p.original_priority - improvement)

            if new_priority != p.priority:
                self.aging_log.append({
                    "time": current_time,
                    "pid": p.pid,
                    "old_priority": p.priority,
                    "new_priority": new_priority
                })
                p.priority = new_priority

    def _select_next_process(self, ready_queue):
        return min(ready_queue, key=lambda p: (p.priority, p.arrival_time))

    def run(self):
        remaining = sorted(self.processes, key=lambda p: p.arrival_time)
        ready_queue = []
        completed = []
        current_time = 0
        n = len(remaining)

        while len(completed) < n:
            while remaining and remaining[0].arrival_time <= current_time:
                ready_queue.append(remaining.pop(0))

            if not ready_queue:
                current_time = remaining[0].arrival_time
                continue

            self._apply_aging(ready_queue, current_time)

            proc = self._select_next_process(ready_queue)
            ready_queue.remove(proc)

            proc.start_time = current_time
            proc.waiting_time = current_time - proc.arrival_time
            run_start = current_time
            current_time += proc.remaining_time
            proc.remaining_time = 0
            proc.completion_time = current_time
            proc.turnaround_time = proc.completion_time - proc.arrival_time

            self.gantt_chart.append({
                "pid": proc.pid,
                "start": run_start,
                "end": current_time,
                "priority_used": proc.priority
            })

            completed.append(proc)

        self.processes = completed
        return completed

    def print_gantt_chart(self):
        print("\nGANTT CHART:")
        line1 = "|"
        line2 = " "
        for seg in self.gantt_chart:
            width = max(len(seg['pid']) + 2, len(str(seg['end'])) + 1)
            line1 += f" {seg['pid']:^{width-2}} |"
            line2 += f"{seg['start']:<{width}}"
        line2 += f"{self.gantt_chart[-1]['end']}"
        print(line1)
        print(line2)

    def print_aging_log(self):
        print("\nLICH SU AGING:")
        if not self.aging_log:
            print("  (khong co su kien aging nao)")
        for e in self.aging_log:
            print(f"  t={e['time']:>3} | {e['pid']} : priority {e['old_priority']} -> {e['new_priority']}")

    def print_results(self):
        print("\nKET QUA:")
        header = f"{'PID':<5}{'Arrival':<9}{'Burst':<7}{'Orig.Pri':<10}{'Start':<7}{'Complete':<10}{'Waiting':<9}{'Turnaround':<11}"
        print(header)
        print("-" * len(header))
        total_wt, total_tat = 0, 0
        for p in self.processes:
            print(f"{p.pid:<5}{p.arrival_time:<9}{p.burst_time:<7}{p.original_priority:<10}"
                  f"{p.start_time:<7}{p.completion_time:<10}{p.waiting_time:<9}{p.turnaround_time:<11}")
            total_wt += p.waiting_time
            total_tat += p.turnaround_time

        n = len(self.processes)
        print(f"\nWaiting time trung binh   = {total_wt/n:.2f}")
        print(f"Turnaround time trung binh = {total_tat/n:.2f}")


if __name__ == "__main__":
    sample_processes = [
        Process(pid="P1", arrival_time=0, burst_time=6, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=2, priority=9),
        Process(pid="P4", arrival_time=3, burst_time=3, priority=1),
        Process(pid="P5", arrival_time=4, burst_time=3, priority=1),
        Process(pid="P6", arrival_time=5, burst_time=3, priority=1),
    ]

    print("=" * 60)
    print("KHONG AGING")
    print("=" * 60)
    sched1 = AgingPriorityScheduler(sample_processes, enable_aging=False)
    sched1.run()
    sched1.print_gantt_chart()
    sched1.print_results()

    print("\n" + "=" * 60)
    print("CO AGING (interval=2, factor=3)")
    print("=" * 60)
    sched2 = AgingPriorityScheduler(sample_processes, aging_interval=2, aging_factor=3, enable_aging=True)
    sched2.run()
    sched2.print_gantt_chart()
    sched2.print_aging_log()
    sched2.print_results()
