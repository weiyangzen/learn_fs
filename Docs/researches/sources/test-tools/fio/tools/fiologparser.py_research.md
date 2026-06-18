# sources/test-tools/fio/tools/fiologparser.py

## Purpose
`fiologparser.py` parses one or more fio time-series logs with non-uniform sample spacing and reports interval sums, averages, full per-series values, all-stat percentiles, or a weighted overall default value.

## Important APIs, Types, and Functions
`parse_args()` defines interval, divisor, output modes, and input files. Output helpers include `print_full()`, `print_sums()`, `print_averages()`, `print_all_stats()`, and `print_default()`. `median()` and `percentile()` support all-stats mode. `TimeSeries` reads a log file into `Sample` objects, tracks the last sample, and provides `get_samples()` and `get_value()` for intervals. `Sample.get_contribution()` weights a sample by interval overlap and divisor.

## Control Flow and State
The main path builds a `TimeSeries` per input file and dispatches to one print mode. Each time series treats a line's timestamp as the sample end and the previous timestamp as its start.

## Dependencies and Integration Points
It uses Python 2/3 compatibility imports and expects fio log lines formatted as `time, value, ...`. It is a post-processing tool for bandwidth, latency, and similar logs.

## Risks and Test Signals
Risks include O(N^2) interval stats noted by a FIXME, Python 3 division bugs in `median()` because list indexes use `/`, empty interval failures in all-stats mode, global `ctx` use inside `TimeSeries.add_sample()` and `Sample.get_contribution()` instead of instance fields, and strict comma-space parsing. Signals are numeric CSV-like output and exceptions for malformed or empty data.
