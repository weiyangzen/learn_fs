# sources/storage-engines/wiredtiger/bench/wtperf/track.c

## Purpose
`track.c` aggregates wtperf operation counts and latency measurements across worker, populate, checkpoint, backup, scan, and flush threads. It also writes latency distribution files for insert, modify, read, and update operations.

## Important APIs, Types, and Functions
Count functions include `sum_pop_ops`, `sum_backup_ops`, `sum_ckpt_ops`, `sum_flush_ops`, `sum_scan_ops`, `sum_insert_ops`, `sum_modify_ops`, `sum_read_ops`, `sum_truncate_ops`, and `sum_update_ops`. Latency functions include `latency_insert`, `latency_modify`, `latency_read`, `latency_update`, `latency_print`, plus static helpers `sum_ops`, `latency_op`, `sum_latency`, and `latency_print_single`.

## Control Flow
Count helpers choose relevant thread arrays and sum `TRACK.ops` fields, often using `offsetof(WTPERF_THREAD, field)` to share logic. `latency_op` computes interval latency by comparing cumulative latency counters against `last_latency*` snapshots, resets min/max for the next interval, and returns average/min/max. Per-operation latency wrappers preserve the last nonzero values to avoid graph discontinuities. `latency_print` builds aggregate latency histograms per operation and writes CSV-like files.

## State and Persistence Behavior
The file mutates `TRACK.last_latency_ops`, `last_latency`, `min_latency`, and `max_latency` while sampling intervals. Static variables inside each latency wrapper remember last displayed values across calls. `latency_print_single` persists files named `latency.insert`, `latency.modify`, `latency.read`, and `latency.update` under `monitor_dir`.

## Dependencies and Integration Points
It depends on `wtperf.h`, `CONFIG_OPTS`, `WTPERF`, `WTPERF_THREAD`, `TRACK`, time conversion macros, and `lprintf`. Monitor/report code in `wtperf.c` calls these helpers to produce periodic metrics and final latency artifacts.

## Risks and Edge Cases
Sampling reads counters concurrently with worker updates; values are approximate by design. Static last latency values are process-global per operation, so multiple wtperf instances in one process would cross-contaminate. `latency_print_single` skips zero buckets and starts millisecond/second loops at 1, so bucket boundary interpretation must match insertion logic. It logs but continues on file-open failure.

## Test Signals
Run workloads with known operation mixes and verify summed counts match `test.stat`. Enable latency tracking, then confirm latency files exist, have headers, monotonic cumulative counts, and plausible total operation counts.
