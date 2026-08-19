import argparse
import csv
from html import escape
from pathlib import Path

from module1_nhaplieu import ProcessInputManager
from module2_nonpreemptive import mo_phong_priority_nonpreemptive
from module3_preemptive import mo_phong_priority_preemptive
from module7_fcfs import mo_phong_fcfs


STATISTICS_COLUMNS = (
    "dataset",
    "status",
    "error",
    "process_count",
    "algorithm",
    "aging_interval",
    "average_wt",
    "average_tat",
    "average_rt",
    "context_switches",
    "total_time",
)

COMPARISON_COLUMNS = (
    "dataset",
    "priority_algorithm",
    "aging_interval",
    "fcfs_wt",
    "priority_wt",
    "wt_difference",
    "fcfs_tat",
    "priority_tat",
    "tat_difference",
    "fcfs_rt",
    "priority_rt",
    "rt_difference",
    "fcfs_context_switches",
    "priority_context_switches",
    "context_switch_difference",
    "better_waiting",
)

SUMMARY_COLUMNS = (
    "algorithm",
    "dataset_count",
    "average_wt",
    "average_tat",
    "average_rt",
    "average_context_switches",
    "average_total_time",
)

DETAIL_COLUMNS = ("PID", "AT", "BT", "PR", "CT", "TAT", "WT", "RT")
INPUT_COLUMNS = ("PID", "AT", "BT", "PR")
GRAPH_METRICS = {
    "average_wt": "Average Waiting Time",
    "average_tat": "Average Turnaround Time",
    "average_rt": "Average Response Time",
    "context_switches": "Context Switches",
}
SUMMARY_GRAPH_METRICS = (
    ("average_wt", "Average WT"),
    ("average_tat", "Average TAT"),
    ("average_rt", "Average RT"),
    ("average_context_switches", "Average Context Switches"),
)
GRAPH_COLORS = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
)


def discover_csv_files(input_path):
    path = Path(input_path)
    if path.is_file():
        if path.suffix.casefold() != ".csv":
            raise ValueError("Input file must have the .csv extension.")
        return [path]
    if not path.is_dir():
        raise ValueError("Input path does not exist.")
    return sorted(
        (item for item in path.iterdir() if item.is_file() and item.suffix.casefold() == ".csv"),
        key=lambda item: item.name.casefold(),
    )


def load_process_csv(file_path):
    manager = ProcessInputManager()
    success, message = manager.load_from_csv(str(file_path))
    if not success:
        raise ValueError(message)
    return manager.get_data()


def _write_csv(file_path, columns, rows):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_processes_csv(processes, output_path):
    _write_csv(output_path, INPUT_COLUMNS, processes)


def save_result_details(result, output_path):
    _write_csv(output_path, DETAIL_COLUMNS, result["processes"])


def build_graph_series(statistics_rows, metric):
    if metric not in GRAPH_METRICS:
        raise ValueError(f"Unsupported graph metric: {metric}")

    datasets = []
    algorithms = []
    values = {}
    for row in statistics_rows:
        if row.get("status") != "success":
            continue
        value = row.get(metric)
        if not isinstance(value, (int, float)):
            continue

        dataset = str(row["dataset"])
        algorithm = str(row["algorithm"])
        if dataset not in datasets:
            datasets.append(dataset)
        if algorithm not in algorithms:
            algorithms.append(algorithm)
        values.setdefault(dataset, {})[algorithm] = float(value)

    return {
        "metric": metric,
        "title": GRAPH_METRICS[metric],
        "datasets": datasets,
        "algorithms": algorithms,
        "values": values,
    }


def build_summary_rows(statistics_rows):
    grouped = {}
    for row in statistics_rows:
        if row.get("status") != "success":
            continue
        algorithm = str(row["algorithm"])
        bucket = grouped.setdefault(
            algorithm,
            {
                "datasets": set(),
                "average_wt": [],
                "average_tat": [],
                "average_rt": [],
                "context_switches": [],
                "total_time": [],
            },
        )
        bucket["datasets"].add(str(row["dataset"]))
        for metric in (
            "average_wt",
            "average_tat",
            "average_rt",
            "context_switches",
            "total_time",
        ):
            value = row.get(metric)
            if isinstance(value, (int, float)):
                bucket[metric].append(float(value))

    summary_rows = []
    for algorithm, bucket in grouped.items():
        def average(metric):
            values = bucket[metric]
            return round(sum(values) / len(values), 2) if values else 0.0

        summary_rows.append({
            "algorithm": algorithm,
            "dataset_count": len(bucket["datasets"]),
            "average_wt": average("average_wt"),
            "average_tat": average("average_tat"),
            "average_rt": average("average_rt"),
            "average_context_switches": average("context_switches"),
            "average_total_time": average("total_time"),
        })
    return summary_rows


def save_svg_graph(statistics_rows, metric, output_path):
    series = build_graph_series(statistics_rows, metric)
    datasets = series["datasets"]
    algorithms = series["algorithms"]
    if not datasets or not algorithms:
        return None

    group_width = max(90, len(algorithms) * 28 + 30)
    width = max(960, 130 + len(datasets) * group_width)
    height = 560
    plot_left = 75
    plot_top = 90
    plot_bottom = 420
    plot_height = plot_bottom - plot_top
    all_values = [
        value
        for dataset_values in series["values"].values()
        for value in dataset_values.values()
    ]
    maximum = max(all_values, default=0.0)
    y_max = maximum * 1.1 if maximum > 0 else 1.0
    bar_width = 20

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        (
            f'<text x="{width / 2:.1f}" y="32" text-anchor="middle" '
            f'font-family="Arial" font-size="22" font-weight="bold">'
            f'{escape(series["title"])}</text>'
        ),
    ]

    legend_x = 80
    for index, algorithm in enumerate(algorithms):
        color = GRAPH_COLORS[index % len(GRAPH_COLORS)]
        svg.append(
            f'<rect x="{legend_x}" y="50" width="14" height="14" fill="{color}"/>'
        )
        svg.append(
            f'<text x="{legend_x + 20}" y="62" font-family="Arial" '
            f'font-size="12">{escape(algorithm)}</text>'
        )
        legend_x += max(150, len(algorithm) * 7 + 45)

    for tick in range(6):
        value = y_max * tick / 5
        y = plot_bottom - plot_height * tick / 5
        svg.append(
            f'<line x1="{plot_left}" y1="{y:.1f}" x2="{width - 30}" '
            f'y2="{y:.1f}" stroke="#DDDDDD" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{plot_left - 10}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Arial" font-size="11">{value:.1f}</text>'
        )

    svg.append(
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" '
        f'y2="{plot_bottom}" stroke="#333333" stroke-width="1.5"/>'
    )
    svg.append(
        f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{width - 30}" '
        f'y2="{plot_bottom}" stroke="#333333" stroke-width="1.5"/>'
    )

    for dataset_index, dataset in enumerate(datasets):
        center = plot_left + 35 + dataset_index * group_width
        total_bar_width = len(algorithms) * bar_width
        first_x = center - total_bar_width / 2
        for algorithm_index, algorithm in enumerate(algorithms):
            value = series["values"].get(dataset, {}).get(algorithm)
            if value is None:
                continue
            color = GRAPH_COLORS[algorithm_index % len(GRAPH_COLORS)]
            bar_height = value / y_max * plot_height
            x = first_x + algorithm_index * bar_width
            y = plot_bottom - bar_height
            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 2}" '
                f'height="{bar_height:.1f}" fill="{color}">'
                f'<title>{escape(dataset)} - {escape(algorithm)}: {value:.2f}</title>'
                '</rect>'
            )
        svg.append(
            f'<text transform="translate({center:.1f},{plot_bottom + 20}) rotate(-45)" '
            f'text-anchor="end" font-family="Arial" font-size="10">'
            f'{escape(dataset)}</text>'
        )

    svg.append('</svg>')
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(svg), encoding="utf-8")
    return str(path.resolve())


def save_summary_svg(summary_rows, output_path):
    if not summary_rows:
        return None

    group_width = 245
    width = max(960, 150 + len(summary_rows) * group_width)
    height = 540
    plot_left = 75
    plot_top = 85
    plot_bottom = 405
    plot_height = plot_bottom - plot_top
    all_values = [
        float(row[metric])
        for row in summary_rows
        for metric, _label in SUMMARY_GRAPH_METRICS
    ]
    maximum = max(all_values, default=0.0)
    y_max = maximum * 1.15 if maximum > 0 else 1.0
    bar_width = 34

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        (
            f'<text x="{width / 2:.1f}" y="30" text-anchor="middle" '
            f'font-family="Arial" font-size="22" font-weight="bold">'
            'Aggregated Metrics Across All Datasets</text>'
        ),
    ]

    legend_x = 75
    for index, (_metric, label) in enumerate(SUMMARY_GRAPH_METRICS):
        color = GRAPH_COLORS[index % len(GRAPH_COLORS)]
        svg.append(
            f'<rect x="{legend_x}" y="48" width="14" height="14" fill="{color}"/>'
        )
        svg.append(
            f'<text x="{legend_x + 20}" y="60" font-family="Arial" '
            f'font-size="12">{escape(label)}</text>'
        )
        legend_x += max(145, len(label) * 7 + 40)

    for tick in range(6):
        value = y_max * tick / 5
        y = plot_bottom - plot_height * tick / 5
        svg.append(
            f'<line x1="{plot_left}" y1="{y:.1f}" x2="{width - 30}" '
            f'y2="{y:.1f}" stroke="#DDDDDD" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{plot_left - 10}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Arial" font-size="11">{value:.1f}</text>'
        )

    svg.append(
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" '
        f'y2="{plot_bottom}" stroke="#333333" stroke-width="1.5"/>'
    )
    svg.append(
        f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{width - 30}" '
        f'y2="{plot_bottom}" stroke="#333333" stroke-width="1.5"/>'
    )

    for algorithm_index, row in enumerate(summary_rows):
        center = plot_left + 70 + algorithm_index * group_width
        total_bar_width = len(SUMMARY_GRAPH_METRICS) * bar_width
        first_x = center - total_bar_width / 2
        for metric_index, (metric, label) in enumerate(SUMMARY_GRAPH_METRICS):
            value = float(row[metric])
            color = GRAPH_COLORS[metric_index % len(GRAPH_COLORS)]
            bar_height = value / y_max * plot_height
            x = first_x + metric_index * bar_width
            y = plot_bottom - bar_height
            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 3}" '
                f'height="{bar_height:.1f}" fill="{color}">'
                f'<title>{escape(row["algorithm"])} - {escape(label)}: {value:.2f}</title>'
                '</rect>'
            )
            svg.append(
                f'<text x="{x + (bar_width - 3) / 2:.1f}" y="{max(plot_top, y - 5):.1f}" '
                f'text-anchor="middle" font-family="Arial" font-size="10">'
                f'{value:.2f}</text>'
            )
        svg.append(
            f'<text transform="translate({center:.1f},{plot_bottom + 28}) rotate(-15)" '
            f'text-anchor="end" font-family="Arial" font-size="11">'
            f'{escape(row["algorithm"])}</text>'
        )
        svg.append(
            f'<text x="{center:.1f}" y="{plot_bottom + 82}" text-anchor="middle" '
            f'font-family="Arial" font-size="10" fill="#666666">'
            f'{row["dataset_count"]} datasets</text>'
        )

    svg.append('</svg>')
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(svg), encoding="utf-8")
    return str(path.resolve())


def save_analysis_graphs(statistics_rows, output_directory, summary_rows=None):
    output = Path(output_directory)
    summary_rows = summary_rows or build_summary_rows(statistics_rows)
    paths = {
        "summary": save_summary_svg(
            summary_rows,
            output / "summary_metrics.svg",
        )
    }
    paths = {name: path for name, path in paths.items() if path}
    for metric in GRAPH_METRICS:
        graph_path = save_svg_graph(
            statistics_rows,
            metric,
            output / f"{metric}.svg",
        )
        if graph_path:
            paths[metric] = graph_path
    return paths


def _result_slug(result):
    return (
        result["algorithm"]
        .casefold()
        .replace(" + ", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def _statistics_row(dataset, result, aging_interval):
    gantt = result.get("gantt", [])
    total_time = gantt[-1]["finish"] if gantt else 0
    return {
        "dataset": dataset,
        "status": "success",
        "error": "",
        "process_count": len(result.get("processes", [])),
        "algorithm": result["algorithm"],
        "aging_interval": aging_interval if "+ Aging" in result["algorithm"] else "",
        "average_wt": round(result["average_waiting"], 2),
        "average_tat": round(result["average_turnaround"], 2),
        "average_rt": round(result["average_response"], 2),
        "context_switches": result["context_switches"],
        "total_time": total_time,
    }


def _comparison_row(dataset, fcfs, priority, aging_interval):
    wt_difference = priority["average_waiting"] - fcfs["average_waiting"]
    if wt_difference < 0:
        better_waiting = "Priority"
    elif wt_difference > 0:
        better_waiting = "FCFS"
    else:
        better_waiting = "Equal"

    return {
        "dataset": dataset,
        "priority_algorithm": priority["algorithm"],
        "aging_interval": aging_interval if "+ Aging" in priority["algorithm"] else "",
        "fcfs_wt": round(fcfs["average_waiting"], 2),
        "priority_wt": round(priority["average_waiting"], 2),
        "wt_difference": round(wt_difference, 2),
        "fcfs_tat": round(fcfs["average_turnaround"], 2),
        "priority_tat": round(priority["average_turnaround"], 2),
        "tat_difference": round(
            priority["average_turnaround"] - fcfs["average_turnaround"], 2
        ),
        "fcfs_rt": round(fcfs["average_response"], 2),
        "priority_rt": round(priority["average_response"], 2),
        "rt_difference": round(
            priority["average_response"] - fcfs["average_response"], 2
        ),
        "fcfs_context_switches": fcfs["context_switches"],
        "priority_context_switches": priority["context_switches"],
        "context_switch_difference": (
            priority["context_switches"] - fcfs["context_switches"]
        ),
        "better_waiting": better_waiting,
    }


def analyze_dataset(processes, priority_mode="both", aging_interval=None):
    if priority_mode not in {"both", "non-preemptive", "preemptive"}:
        raise ValueError("priority_mode must be both, non-preemptive or preemptive.")
    if aging_interval is not None and aging_interval <= 0:
        raise ValueError("Aging interval must be greater than 0.")

    results = [mo_phong_fcfs(processes)]
    if priority_mode in {"both", "non-preemptive"}:
        results.append(mo_phong_priority_nonpreemptive(processes, aging_interval))
    if priority_mode in {"both", "preemptive"}:
        results.append(mo_phong_priority_preemptive(processes, aging_interval))
    return results


def analyze_path(input_path, output_directory, priority_mode="both", aging_interval=None):
    csv_files = discover_csv_files(input_path)
    if not csv_files:
        raise ValueError("No CSV files were found in the selected input path.")

    output = Path(output_directory)
    normalized_directory = output / "normalized"
    details_directory = output / "details"
    statistics_rows = []
    comparison_rows = []
    successful_files = 0

    for csv_file in csv_files:
        dataset = csv_file.stem
        try:
            processes = load_process_csv(csv_file)
            if not processes:
                raise ValueError("CSV file contains no valid processes.")

            save_processes_csv(processes, normalized_directory / csv_file.name)
            results = analyze_dataset(processes, priority_mode, aging_interval)
            fcfs = results[0]

            for result in results:
                statistics_rows.append(
                    _statistics_row(dataset, result, aging_interval)
                )
                save_result_details(
                    result,
                    details_directory / f"{dataset}__{_result_slug(result)}.csv",
                )

            for priority in results[1:]:
                comparison_rows.append(
                    _comparison_row(dataset, fcfs, priority, aging_interval)
                )
            successful_files += 1
        except (OSError, TypeError, ValueError) as error:
            statistics_rows.append({
                "dataset": dataset,
                "status": "error",
                "error": str(error),
                "process_count": 0,
                "algorithm": "",
                "aging_interval": aging_interval or "",
                "average_wt": "",
                "average_tat": "",
                "average_rt": "",
                "context_switches": "",
                "total_time": "",
            })

    statistics_path = output / "statistics.csv"
    comparison_path = output / "comparison.csv"
    summary_path = output / "summary.csv"
    _write_csv(statistics_path, STATISTICS_COLUMNS, statistics_rows)
    _write_csv(comparison_path, COMPARISON_COLUMNS, comparison_rows)
    summary_rows = build_summary_rows(statistics_rows)
    _write_csv(summary_path, SUMMARY_COLUMNS, summary_rows)
    graph_paths = save_analysis_graphs(
        statistics_rows,
        output / "graphs",
        summary_rows,
    )

    return {
        "total_files": len(csv_files),
        "successful_files": successful_files,
        "failed_files": len(csv_files) - successful_files,
        "statistics": statistics_rows,
        "comparisons": comparison_rows,
        "summary": summary_rows,
        "statistics_path": str(statistics_path.resolve()),
        "comparison_path": str(comparison_path.resolve()),
        "summary_path": str(summary_path.resolve()),
        "graph_paths": graph_paths,
    }


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Batch analysis for FCFS and Priority scheduling CSV files."
    )
    parser.add_argument("--input", required=True, help="CSV file or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--priority-mode",
        choices=("both", "non-preemptive", "preemptive"),
        default="both",
    )
    parser.add_argument("--aging", type=int, default=None)
    return parser


def main():
    arguments = _build_parser().parse_args()
    report = analyze_path(
        arguments.input,
        arguments.output,
        priority_mode=arguments.priority_mode,
        aging_interval=arguments.aging,
    )
    print(
        f"Processed {report['successful_files']}/{report['total_files']} CSV files."
    )
    print(f"Statistics: {report['statistics_path']}")
    print(f"Comparison: {report['comparison_path']}")
    print(f"Summary: {report['summary_path']}")
    if report["graph_paths"]:
        print(f"Graphs: {Path(next(iter(report['graph_paths'].values()))).parent}")


if __name__ == "__main__":
    main()
