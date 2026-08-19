import copy
import csv
import random
from typing import List, Tuple, Dict, Any


class ProcessInputManager:
    def __init__(self):
        self.process_list: List[Dict[str, Any]] = []

    def validate(self, pid: str, at: int, bt: int, pr: int) -> Tuple[bool, str]:
        if not pid or str(pid).strip() == "":
            return False, "Error: PID cannot be empty."

        cleaned_pid = str(pid).strip()
        if any(p["PID"] == cleaned_pid for p in self.process_list):
            return False, f"Error: PID '{cleaned_pid}' already exists."

        if at < 0:
            return False, "Error: Arrival Time (AT) must be greater than or equal to 0."

        if bt <= 0:
            return False, "Error: Burst Time (BT) must be a positive integer (> 0)."

        if pr < 0:
            return False, "Error: Priority (PR) cannot be negative."

        return True, ""

    def add_process(self, pid: str, at: int, bt: int, pr: int) -> Tuple[bool, str]:
        is_valid, error_msg = self.validate(pid, at, bt, pr)
        if not is_valid:
            return False, error_msg

        self.process_list.append({
            "PID": str(pid).strip(),
            "AT": int(at),
            "BT": int(bt),
            "PR": int(pr)
        })
        return True, "Process added successfully."

    def remove_process(self, pid: str) -> bool:
        initial_length = len(self.process_list)
        self.process_list = [p for p in self.process_list if p["PID"] != str(pid).strip()]
        return len(self.process_list) < initial_length

    def clear(self) -> None:
        self.process_list.clear()

    def load_from_csv(self, file_path: str) -> Tuple[bool, str]:
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip CSV header

                self.clear()
                for row_idx, row in enumerate(reader, start=2):
                    if not row or len(row) < 4:
                        continue

                    pid, at_str, bt_str, pr_str = (
                        row[0].strip(),
                        row[1].strip(),
                        row[2].strip(),
                        row[3].strip()
                    )

                    try:
                        at = int(at_str)
                        bt = int(bt_str)
                        pr = int(pr_str)

                        success, msg = self.add_process(pid, at, bt, pr)
                        if not success:
                            return False, f"Row {row_idx}: {msg}"
                    except ValueError:
                        return False, f"Row {row_idx}: Invalid numeric format."

            return True, "CSV file loaded successfully."
        except Exception as e:
            return False, f"Failed to read file: {str(e)}"

    def generate_random(
        self,
        n: int = 5,
        max_at: int = 10,
        max_bt: int = 10,
        max_pr: int = 5
    ) -> List[Dict[str, Any]]:
        self.clear()
        for i in range(1, n + 1):
            self.process_list.append({
                "PID": f"P{i}",
                "AT": random.randint(0, max_at),
                "BT": random.randint(1, max_bt),
                "PR": random.randint(0, max_pr)
            })
        return self.get_data()

    def get_data(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self.process_list)

    def get_count(self) -> int:
        return len(self.process_list)


def get_initial_processes(
    source: str = "dummy",
    file_path: str = "input.csv",
    n: int = 5,
    max_at: int = 10,
    max_bt: int = 10,
    max_pr: int = 5
) -> List[Dict[str, Any]]:
    manager = ProcessInputManager()

    if source == "random":
        return manager.generate_random(n=n, max_at=max_at, max_bt=max_bt, max_pr=max_pr)
    elif source == "csv":
        manager.load_from_csv(file_path)
        return manager.get_data()
    else:
        # Default fallback to dummy_data.py
        try:
            from dummy_data import danh_sach_test
            return copy.deepcopy(danh_sach_test)
        except ImportError:
            
            return [
                {"PID": "P1", "AT": 0, "BT": 5, "PR": 2},
                {"PID": "P2", "AT": 1, "BT": 3, "PR": 1},
                {"PID": "P3", "AT": 2, "BT": 8, "PR": 3},
                {"PID": "P4", "AT": 4, "BT": 2, "PR": 4}
            ]
