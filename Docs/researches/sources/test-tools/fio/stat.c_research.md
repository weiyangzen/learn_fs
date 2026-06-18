# sources/test-tools/fio/stat.c

## Purpose
`stat.c` is fio's main statistics engine. It collects per-I/O latency, bandwidth, IOPS, depth, error, CPU, disk-util, steady-state, and trim-block-lifetime samples; aggregates them across jobs/groups; renders normal, terse, and JSON output; and in backend mode serializes final stats to the server transport.

## Important APIs, Types, And Functions
Public collection APIs include `add_clat_sample()`, `add_slat_sample()`, `add_lat_sample()`, `add_bw_sample()`, `add_iops_sample()`, `add_sync_clat_sample()`, `add_agg_sample()`, `calc_log_samples()`, `finalize_logs()`, `regrow_logs()`, and `reset_io_stats()`. Public reporting and aggregation APIs include `__show_run_stats()`, `__show_running_run_stats()`, `show_running_run_stats()`, `check_for_running_stats()`, `show_thread_status()`, `show_group_stats()`, `sum_thread_stats()`, `sum_group_stats()`, `init_thread_stat()`, `init_group_run_stat()`, `alloc_clat_prio_stat_ddir()`, `free_clat_prio_stats()`, and disk-util JSON/text helpers.

Core statistical helpers include `add_stat_sample()` for online mean/variance, `__sum_stat()` for parallel variance merge, `plat_val_to_idx()` and `plat_idx_to_val()` for latency percentile buckets, `calc_clat_percentiles()`, `stat_calc_dist()`, latency distribution calculators, and block lifetime percentile helpers.

## Control Flow
I/O paths call `add_slat_sample()`, `add_clat_sample()`, `add_lat_sample()`, `add_bw_sample()`, and `add_iops_sample()` as work is issued/completed. These update `thread_stat` fields, percentile histograms, per-priority stats, and optional log buffers. Periodic logging flows through `calc_log_samples()`, which samples bandwidth and IOPS windows when threads are in logging states and returns the next wakeup delay. `finalize_logs()` flushes averaged log windows at job end.

Final reporting starts in `__show_run_stats()`: it allocates one `group_run_stats` per group and enough `thread_stat` slots for either per-thread or group-reporting mode, initializes per-priority behavior, folds each `thread_data` into the selected aggregate, builds group bandwidth/runtime summaries, and writes normal/terse/JSON buffers or server messages depending on `is_backend`. Running-stat snapshots use `__show_running_run_stats()`, which asks workers to refresh rusage outside `stat_sem`, temporarily adds current runtime deltas, calls `__show_run_stats()`, then rolls back temporary runtime changes.

## State And Persistence Behavior
`stat_sem` is a shared semaphore protecting out-of-band stat snapshots. `agg_io_log[]`, `write_bw_log`, fio global thread lists, disk lists, output format globals, and status-file state are external/global integration points. Persistent behavior is limited to the trigger file `/tmp/fio-dump-status` or `$TMPDIR/fio-dump-status`: when present, it is unlinked and causes running stats to be emitted. Logs are accumulated in memory as `struct io_logs` chunks and later written/transmitted by iolog code/server code.

## Dependencies And Integration Points
The file integrates with `fio.h`, `iolog`, `server.c`, `diskutil`, JSON output, helper thread signaling, idletime, zbd status, `steadystate`, `smalloc`, OS rusage, and fio job/thread data. In backend mode it calls server send functions instead of printing locally. It relies on `stat.h` for struct layout shared with network payloads.

## Risks And Edge Cases
Several paths assume initialized min values and valid sample counts; direct struct zeroing without `init_thread_stat()` would skew minima. `stat_calc_lat_nu()` divides by total without an explicit zero guard after `stat_calc_lat()`. Per-priority aggregation allocates with `smalloc`; callers must free with `free_clat_prio_stats()`. `calc_block_percentiles()` computes percentile indexes without an obvious upper-bound clamp for 100% edge cases. Running stats temporarily mutate thread runtimes and require careful rollback under `stat_sem`. Output compatibility is fragile: terse field order and JSON key names are externally consumed. Histogram log code stores pointers requiring later cleanup in iolog processing.

## Test Signals
Tests should cover percentile bucket round trips, percentile sorting, online variance and merged variance, group reporting with mixed read/write/trim, per-priority stats aggregation, terse versions 2-5, JSON and JSON+ bins, steady-state data rendering, disk-util slave aggregation, status-file-triggered running stats, averaged log windows, compressed/uncompressed iolog transfer integration, and async/offload locking paths.
