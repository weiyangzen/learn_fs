# sources/test-tools/fio/tools/hist/fio-histo-log-pctiles.py

## Purpose
`fio-histo-log-pctiles.py` parses fio histogram logs without pandas, aligns multiple thread logs to a common time quantum, aggregates buckets, and reports latency percentiles per time interval. It can also run embedded unit tests via the `UNITTEST` environment variable.

## Important APIs, Types, and Functions
`FioHistoLogExc` models parse errors. `parse_hist_file()` validates CSV histogram records, enforces nonnegative integers, direction values, monotonic timestamps per direction, block-size limits, and expected bucket counts, then estimates start/end timestamps. `time_ranges()` maps fio v2/v3 histogram bucket indexes to latency ranges. `get_time_intervals()` computes quantum count. `align_histo_log()` weights raw histogram buckets into aligned intervals by overlap fraction. `add_to_histo_from()`, `get_samples()`, and `get_pctiles()` aggregate and interpolate percentile results. `compute_percentiles_from_logs()` is the CLI entry point.

## Control Flow and State
CLI arguments select fio version, bucket groups/bits, requested percentiles, time quantum, optional log interval, output unit, and files. The script parses each log, chooses the time range common to all threads, aligns each per-thread histogram, sums them into `all_threads_histograms`, and prints CSV-like percentile rows. Unit tests cover parsing validation, bucket range computation, alignment, and percentile interpolation.

## Dependencies and Integration Points
It depends on Python 2/3-compatible standard libraries plus optional `unittest2`. It consumes fio histogram log format and mirrors fio `stat.h` bucket semantics. Output can feed analysis pipelines.

## Risks and Test Signals
Risks include assumptions that all threads run the same workload duration, limited read/write separation for randrw, fragile next-record direction matching, missing `nsec` output-unit handling, and possible exceptions when only one epoch-style record lacks `log_hist_msec`. Signals are explicit parse errors, unit tests, printed parameter echo, and percentile rows with sample counts.
