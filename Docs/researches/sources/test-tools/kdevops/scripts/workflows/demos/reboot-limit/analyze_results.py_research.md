# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/analyze_results.py

## Purpose
Analyzes reboot-limit workflow results and optionally generates boot-time graphs for regular and kexec reboot comparisons.

## Important APIs
`RebootLimitAnalyzer` holds `hosts_data`, `regular_data`, `kexec_data`, and `comparison_mode`. Key methods include `parse_systemd_analyze_line()`, `load_host_data()`, `load_all_data()`, `calculate_statistics()`, `plot_boot_times()`, `plot_single_mode_analysis()`, `plot_comparison_analysis()`, `print_summary()`, `print_single_mode_summary()`, and `print_comparison_summary()`.

## Control flow
`main()` accepts a results directory, output path, and `--no-plot`. The analyzer detects comparison mode when `regular/` and `kexec/` subdirectories exist; otherwise each host subdirectory is loaded directly. It parses `reboot-count.txt` and `systemctl-analyze.txt`, prints textual statistics, and generates matplotlib PNG plots unless disabled.

## State and persistence
Reads workflow results and writes a PNG graph, creating the output directory if needed. It exits 0 when no data exists, treating that as a normal pre-run state.

## Dependencies and integration
Uses Python standard library plus `matplotlib`. It is tied to reboot-limit result layout and systemd-analyze output formats with and without initrd.

## Risks and test signals
The parser only accepts seconds with `s`, not `ms` or `min`. Comparison plot combines all hosts into aggregate series, which can obscure host-level variance. Test with generated sample data, no-data directories, comparison mode, and `--no-plot` on hosts without matplotlib.
