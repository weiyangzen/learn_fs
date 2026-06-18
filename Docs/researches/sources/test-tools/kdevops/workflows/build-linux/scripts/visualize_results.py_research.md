# sources/test-tools/kdevops/workflows/build-linux/scripts/visualize_results.py

## Purpose
Loads build-linux result summaries, raw timings, and optional monitoring artifacts; generates embedded matplotlib charts and an HTML performance report; and consolidates shareable HTML/PNG output.

## Important APIs, Types, and Functions
Important functions are `load_all_results`, chart creators, `generate_monitoring_section`, `generate_html_report`, `consolidate_html_output`, and `main`. Data is stored in summary/timing/monitoring dictionaries.

## Control Flow
`main()` validates the results directory, loads data, requires summaries, optionally generates HTML, copies it to `html/index.html`, copies monitoring PNGs, then prints a console summary.

## State and Persistence Behavior
Reads `*_summary_*.json`, `*_build_times_*.json`, and monitoring files. Writes `build_performance_report.html`, creates `html/`, and copies monitoring plots.

## Dependencies and Integration Points
Matplotlib/numpy are optional but needed for charts. Integrates with build-linux Makefile, result collection, and monitoring roles.

## Risks and Edge Cases
Top summary success-rate calculation divides by zero when `total_builds == 0`. HTML values are not escaped. Filesystem detection is hostname-based. Missing matplotlib degrades chart sections.

## Test Signals
Test no summaries, zero builds, all-failed hosts, missing matplotlib, monitoring plot variants, and XFS/ext4/btrfs/unknown hostnames. Verify `html/index.html`.
