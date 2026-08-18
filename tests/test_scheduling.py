from __future__ import annotations

import unittest

from model import Process
from service.misc.scheduling import build_comparison, simulate_algorithm


def sample_processes() -> tuple[Process, ...]:
    return (
        Process("P1", 0, 5, 3),
        Process("P2", 1, 2, 1),
        Process("P3", 2, 1, 2),
    )


def segments(run: object) -> list[tuple[str, int, int]]:
    result = run.result  # type: ignore[attr-defined]
    return [(segment.pid, segment.start, segment.end) for segment in result.segments]


class SchedulingTests(unittest.TestCase):
    def test_fcfs_order(self) -> None:
        run = simulate_algorithm(sample_processes(), "fcfs")
        self.assertEqual(segments(run), [("P1", 0, 5), ("P2", 5, 7), ("P3", 7, 8)])

    def test_sjf_chooses_shortest_ready_job(self) -> None:
        run = simulate_algorithm(sample_processes(), "sjf")
        self.assertEqual(segments(run), [("P1", 0, 5), ("P3", 5, 6), ("P2", 6, 8)])

    def test_srtf_preempts(self) -> None:
        run = simulate_algorithm(sample_processes(), "srtf")
        self.assertEqual(
            segments(run),
            [("P1", 0, 1), ("P2", 1, 3), ("P3", 3, 4), ("P1", 4, 8)],
        )
        self.assertTrue(any(step.event == "PREEMPTED" for step in run.steps))

    def test_priority_preemptive(self) -> None:
        run = simulate_algorithm(sample_processes(), "priority_preemptive")
        self.assertEqual(
            segments(run),
            [("P1", 0, 1), ("P2", 1, 3), ("P3", 3, 4), ("P1", 4, 8)],
        )

    def test_round_robin_quantum_two(self) -> None:
        run = simulate_algorithm(sample_processes(), "round_robin", quantum=2)
        self.assertEqual(
            segments(run),
            [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 5), ("P1", 5, 8)],
        )

    def test_comparison_contains_five_algorithms(self) -> None:
        comparison = build_comparison(sample_processes(), priority_preemptive=True, quantum=2)
        self.assertEqual(len(comparison), 5)
        self.assertEqual(
            [item.result.algorithm.split()[0] for item in comparison],
            ["FCFS", "SJF", "SRTF", "Priority", "Round"],
        )


if __name__ == "__main__":
    unittest.main()
