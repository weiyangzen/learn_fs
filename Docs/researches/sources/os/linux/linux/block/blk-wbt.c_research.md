# File Research: sources/os/linux/linux/block/blk-wbt.c

## Scope

This file implements buffered writeback throttling as an `rq_qos` policy. It monitors read/write latency through block statistics and dynamically limits writeback, discard, and swap write inflight depth to protect read latency.

## Core State

- `struct rq_wb` stores configured background/normal writeback depths, enable state, unknown-window count, latency windows, blk-stat callback, sync read tracking, last read issue/completion times, minimum target latency, rq-qos object, per-class wait queues, and adaptive queue depth state.
- WBT flags distinguish tracked writes, reads, swap writes, and discards.
- WBT has separate wait classes for background writes, swap writes, and discards.
- Enable state distinguishes default on/off from manual sysfs on/off.

## Control Flow

- Bio/request hooks:
  - `wbt_wait()` classifies a bio; reads update recent I/O timestamps, tracked writes block in `rq_qos_wait()` if inflight would exceed the current limit, and the latency window timer is armed as needed.
  - `wbt_track()` stores WBT flags in the request.
  - `wbt_issue()` records one sync read issue timestamp/cookie to detect a read stuck behind writes before completion samples arrive.
  - `wbt_done()` clears request state, accounts tracked write completion through `__wbt_done()`, and updates read completion timestamps.
  - `wbt_cleanup()` drops an inflight count for bios that are cleaned up before normal request completion.
- Latency adaptation:
  - `wb_timer_fn()` evaluates the current `blk_rq_stat` samples.
  - `latency_exceeded()` returns `LAT_EXCEEDED`, `LAT_OK`, `LAT_UNKNOWN`, or `LAT_UNKNOWN_WRITES` based on sync issue latency, read/write sample validity, and minimum read latency.
  - `scale_down()` reduces depth on exceeded latency; `scale_up()` raises depth or allows negative scale steps for write-only periods.
  - `rwb_arm_timer()` shrinks the monitoring window for positive throttling steps and keeps the default window for negative steps.
- Limits:
  - `get_limit()` gives high-priority/swap/sync writeback up to max depth, background or recent-read cases the background depth, discards background depth, and normal buffered writes the normal depth.
  - `calc_wb_limits()` derives normal/background depth from adaptive max depth and target latency.

## Lifecycle and Interfaces

- `wbt_alloc()` creates `rq_wb` and a two-bucket blk-stat callback using `wbt_data_dir()`.
- `wbt_init()` initializes wait queues, defaults, rq-depth state, registers rq-qos ops, and attaches the stats callback.
- `wbt_init_enable_default()`, `wbt_enable_default()`, and `wbt_disable_default()` manage default enablement.
- `wbt_set_lat()` handles sysfs latency changes, allocating WBT if absent, freezing/quiescing the queue around enable/disable or latency updates, and registering debugfs rq-qos files.
- `wbt_get_min_lat()` and `wbt_disabled()` are used by sysfs show paths.

## Dependencies and Invariants

- Depends on `blk-stat.h`, `blk-rq-qos`, request queue depth helpers, backing device dirty throttling timestamps, and WBT tracepoints.
- WBT only throttles writes/discards selected by `wbt_should_throttle()`; direct I/O writes marked sync+idle bypass it.
- Request pointers used as `sync_cookie` are never dereferenced after storage; only address equality is used.
- Queue freeze/quiesce is required when sysfs latency changes can enable or disable WBT with I/O in flight.
