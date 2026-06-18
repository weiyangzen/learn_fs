# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-multi-fs-compare.py

Purpose: Aggregates fio JSON results across filesystem configurations and produces overview, block-size heatmap, IO-depth scaling, and CSV summary artifacts.

Key APIs and flow: `collect_results()` recursively finds JSON files, infers filesystem from path or hostname-like path components, parses metrics via `parse_fio_json()`, and returns a DataFrame. `create_filesystem_comparison_plots()` groups by filesystem, plots average bandwidth/IOPS/latency, optional block-size heatmaps, optional IO-depth scaling, and writes `filesystem_performance_summary.csv`.

State, dependencies, integration: Reads `**/*.json`, writes several fixed-name PNGs and one CSV under the output directory. Depends on pandas, matplotlib, seaborn, numpy. It integrates with fio multi-filesystem result trees.

Risks and test signals: Filesystem inference is heuristic and path-order dependent; `--title` is parsed but unused; first fio job only; `iodepth` is stored as a string until plotting. Tests should cover nested host directories, unknown filesystems, missing job options, single-filesystem runs, and no-result exits.
