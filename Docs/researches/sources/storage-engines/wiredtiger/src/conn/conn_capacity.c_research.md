# sources/storage-engines/wiredtiger/src/conn/conn_capacity.c

## Purpose
This file implements WiredTiger's connection-level I/O capacity controller. It parses `io_capacity.total`, derives per-subsystem capacities, starts and stops the capacity server thread, asynchronously flushes accumulated writes, and throttles read, log, checkpoint, and eviction I/O by assigning time reservations proportional to byte counts.

## Important APIs, Types, and Functions
`__wti_capacity_server_create` and `__wti_capacity_server_destroy` are the connection lifecycle entry points. `__capacity_config` validates `io_capacity.total`, sets `WT_THROTTLE.total`, derives `ckpt`, `evict`, `log`, and `read` capacities via `WT_CAPACITY_SYS`, and publishes `capacity_threshold`.

`__capacity_server_start` opens the `capacity-server` internal session, allocates `conn->capacity.cond`, sets `WT_CONN_SERVER_CAPACITY`, and creates the server thread. `__capacity_server` waits on the condition, calls `__wt_fsync_background` after accumulated non-read writes cross the configured threshold, records `fsync_all_time`, and resets `cap->written`.

`__wt_capacity_throttle` is the hot path called by block, block-cache, file-handle, and log write/read code. It maps `WT_THROTTLE_CKPT`, `WT_THROTTLE_EVICT`, `WT_THROTTLE_LOG`, and `WT_THROTTLE_READ` to per-subsystem reservation clocks and statistics. `__capacity_reserve` atomically advances a reservation clock by `WT_RESERVATION_NS(bytes, capacity)`.

## Control Flow and Behavior
Startup first destroys any existing server during reconfigure, then parses capacity settings. In-memory, read-only, and platforms without background fsync skip thread creation even when a total capacity is configured. A nonzero capacity starts a dedicated internal session and condition variable.

The server loop sleeps until signalled, with a periodic one-second wakeup as a missed-signal guard. It exits when `WT_CONN_SERVER_CAPACITY` is cleared. Otherwise it ignores wakeups until `cap->written >= cap->threshold`, performs a background fsync, updates timing stats, and clears the written counter.

Throttle calls return immediately when total capacity is disabled, the selected subsystem has zero capacity, or the connection is recovering. Non-read calls add to `cap->written` and may signal the server. The caller gets a current wall-clock nanosecond timestamp, reserves slots in both the subsystem reservation clock and the total reservation clock, optionally steals unused reservation time from another idle subsystem, then sleeps only when the chosen reservation lies in the future and exceeds `WT_CAPACITY_SLEEP_CUTOFF_US`.

## State and Persistence Behavior
All capacity state is in memory under `conn->capacity.throttle`: configured byte rates, reservation clocks, written byte counters, signal state, and thread/session handles. There is no durable metadata. Reconfiguration resets the server and rewrites the throttle values. The reservation clocks deliberately self-heal if a reservation is more than one second behind wall clock, preventing stale reservation values from causing extreme future or past accounting after idle periods.

Statistics are the observable persistent signal during process lifetime: bytes per subsystem, total bytes written, wait time per subsystem or total cap, `capacity_threshold`, and fsync timing. The background fsync behavior affects durability pressure indirectly but does not create an explicit on-disk record.

## Dependencies and Integration Points
This code integrates with `wiredtiger_open` and reconfigure capacity settings, connection server flags, internal sessions, WT condition variables and thread APIs, atomic operations, connection stats, `__wt_fsync_background`, and I/O call sites such as `block_read.c`, `block_disagg_mgr.c`, `os_fhandle.c`, `block_mgr.c`, and `log.c`.

It relies on capacity constants and macros from WiredTiger internals: `WT_THROTTLE_MIN`, `WT_CAPACITY_SYS`, `WT_CAPACITY_PCT`, `WT_CAPACITY_MIN_THRESHOLD`, `WT_CAPACITY_SLEEP_CUTOFF_US`, `WT_BILLION`, and `WT_STEAL_FRACTION`.

## Risks
The throttle path is lock-free and heavily atomic, so reservation arithmetic must avoid overflow and inconsistent reservation rollback. The code asserts writes are below `16 * WT_GIGABYTE`; larger byte counts could overflow nanosecond calculations. Stealing capacity has a race-sensitive CAS path that subtracts the caller's prior reservation before retrying. Bugs there can undercount or overcount future sleep.

The server's `signalled` flag is not a replacement for the condition variable, so missed or reordered signals are mitigated by the timed wait. Reconfigure destroys and recreates the thread to avoid concurrent config mutation, but callers of `__wt_capacity_throttle` can still observe new `total` values while old reservation clocks remain in memory. Read-only, in-memory, recovery, and unsupported background fsync cases are intentionally no-op paths and should remain so.

## Test Signals
Direct signals are `test_reconfig01.py` for `io_capacity` reconfiguration and minimum validation, `test_txn24.py` for eviction capacity byte stats, and stats counters for `capacity_bytes_*`, `capacity_time_*`, `capacity_threshold`, and `fsync_all_time`. Workloads that configure low capacity should show sleep-time accumulation and lower write throughput; disabled capacity should show no throttling. Recovery tests should verify no capacity sleep during `WT_CONN_RECOVERING`.
