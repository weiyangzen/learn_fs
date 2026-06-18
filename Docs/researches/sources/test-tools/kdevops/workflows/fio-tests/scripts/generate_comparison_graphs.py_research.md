# sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comparison_graphs.py

## Purpose
Generates multi-filesystem fio comparison PNGs for IOPS, bandwidth, block-size impact, IO-depth scaling, and a dashboard.

## Important APIs, Types, and Functions
Functions are `load_fio_results`, `create_comparison_bar_chart`, `create_block_size_comparison`, `create_iodepth_scaling`, `create_summary_dashboard`, and `main`. Data is nested by filesystem and test key.

## Control Flow
`main()` validates `<results_directory>`, loads hard-coded XFS/ext4/btrfs result directories, creates `graphs/`, then writes four PNG charts. Loading parses metrics from `results_*.json` filenames and the first fio job.

## State and Persistence Behavior
Reads JSON files and writes `multi_filesystem_comparison.png`, `block_size_comparison.png`, `iodepth_scaling.png`, and `performance_dashboard.png`.

## Dependencies and Integration Points
Requires matplotlib and numpy. Integrates with fio multi-filesystem result layout and comprehensive analysis.

## Risks and Edge Cases
Directory names and filesystem list are hard-coded, ignoring other enabled variants. Label offsets and percentage calculations can divide by zero when all values are zero. Some imports are unused.

## Test Signals
Test missing directories, one filesystem, all-zero results, malformed filenames, write workloads, and all configured variants. Assert output PNGs are non-empty.
