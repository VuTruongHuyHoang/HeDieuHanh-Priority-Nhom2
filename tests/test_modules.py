from __future__ import annotations

import unittest

from service.module.module1_nhaplieu import chuan_hoa_danh_sach, tao_tien_trinh
from service.module.module2_nonpreemptive import mo_phong_priority_nonpreemptive
from service.module.module3_preemptive import mo_phong_priority_preemptive
from service.module.module4_aging import tinh_priority_hieu_dung
from service.module.module5_bangketqua import build_result_view_data
from service.module.module7_fcfs import mo_phong_fcfs
from service.module.module8_mainui import DETAIL_ALGORITHMS, _detail_algorithm_key


class FixedModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processes = chuan_hoa_danh_sach(
            [
                {"pid": "P1", "arrival": 0, "burst": 4, "priority": 2},
                {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
                {"pid": "P3", "arrival": 2, "burst": 2, "priority": 3},
            ]
        )

    def test_input_module_validates_duplicate_pid(self) -> None:
        with self.assertRaisesRegex(ValueError, "PID"):
            chuan_hoa_danh_sach(
                [tao_tien_trinh("P1", 0, 1, 1), tao_tien_trinh("p1", 1, 1, 2)]
            )

    def test_priority_adapters_and_fcfs(self) -> None:
        self.assertEqual(
            mo_phong_priority_nonpreemptive(self.processes).result.algorithm,
            "Priority Non-Preemptive",
        )
        self.assertEqual(
            mo_phong_priority_preemptive(self.processes).result.algorithm,
            "Priority Preemptive",
        )
        self.assertEqual(mo_phong_fcfs(self.processes).result.algorithm, "FCFS")

    def test_aging_reduces_numeric_priority(self) -> None:
        process = tao_tien_trinh("P1", 0, 1, 5)
        self.assertEqual(
            tinh_priority_hieu_dung(process, current_time=9, aging_interval=3),
            2,
        )

    def test_result_module_returns_neutral_payload(self) -> None:
        result = mo_phong_fcfs(self.processes).result
        payload = build_result_view_data(result)
        self.assertEqual(payload["algorithm"], "FCFS")
        self.assertEqual(len(payload["metrics"]), 3)
        self.assertIn("Avg WT=", payload["summary"])

    def test_detail_simulation_only_exposes_priority_and_fcfs(self) -> None:
        self.assertEqual(DETAIL_ALGORITHMS, ("Priority", "FCFS"))
        self.assertEqual(_detail_algorithm_key("FCFS", "Preemptive"), "fcfs")
        self.assertEqual(
            _detail_algorithm_key("Priority", "Preemptive"),
            "priority_preemptive",
        )
        self.assertEqual(
            _detail_algorithm_key("Priority", "Non-Preemptive"),
            "priority_non_preemptive",
        )


if __name__ == "__main__":
    unittest.main()
