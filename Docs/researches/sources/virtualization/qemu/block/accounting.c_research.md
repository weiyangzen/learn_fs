# File Research: sources/virtualization/qemu/block/accounting.c

This file implements QEMU block-layer I/O accounting: operation counts, byte counts, failed/invalid/merged request counters, latency totals, timed moving averages, idle-time calculation, and optional latency histograms.

Key entry points:
- `block_acct_init()` initializes the mutex, selects virtual clock under qtest, and defaults `account_invalid`/`account_failed` to true.
- `block_acct_setup()` applies `OnOffAuto` policy for invalid/failed accounting and installs timed-stat intervals via `block_acct_add_interval()`.
- `block_acct_start()` records bytes, start timestamp, and I/O type in a `BlockAcctCookie`.
- `block_acct_done()` and `block_acct_failed()` both route to `block_account_one_io()`, which updates counters, histograms, total latency, last-access time, and interval averages under `stats->lock`.
- `block_acct_invalid()` counts invalid submissions without adding latency because no actual I/O happened.
- `block_latency_histogram_set()` validates strictly increasing bucket boundaries and replaces the histogram arrays for a specific `BlockAcctType`.
- `block_acct_queue_depth()` derives queue depth as timed latency sum divided by elapsed interval time.

Concurrency model:
- Mutable `BlockAcctStats` fields are protected by `stats->lock`.
- Histogram updates occur inside the same accounting lock when called from request completion.
- Interval list mutation is locked during insertion, but iteration helper `block_acct_interval_next()` itself does not lock, so callers must already be in a safe context.

Notable behavior:
- qtest forces deterministic latency (`qtest_latency_ns`) for stable tests.
- Failed I/O increments `failed_ops` and only contributes latency if `account_failed` is enabled.
- Successful I/O increments bytes and operation count.
- Invalid I/O may update `last_access_time_ns` depending on `account_invalid`.
- `cookie->type` is reset to `BLOCK_ACCT_NONE` after completion to avoid double-accounting.

Filesystem/block relevance:
- This is observability infrastructure for QEMU block devices rather than a storage format or driver.
- It feeds monitor-visible block statistics and timing metrics used to reason about guest-visible disk behavior, throttling, and error handling.

Potential pitfalls:
- `block_acct_idle_time_ns()` reads `last_access_time_ns` without taking the stats lock, so consumers should treat it as an approximate statistic.
- `block_acct_queue_depth()` divides by `elapsed`; correctness relies on `timed_average_sum()` providing nonzero elapsed time.
