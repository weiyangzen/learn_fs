# File Research: sources/virtualization/qemu/block/null.c

## Purpose
Implements QEMU’s synthetic null block drivers: `null-co` for coroutine callbacks and `null-aio` for AIO callbacks. These drivers provide a configurable-size block node that discards writes, optionally returns zeroes on reads, and can emulate completion latency.

## Main Entry Points
- `null_open()` parses `size`, `latency-ns`, and `read-zeroes` runtime options and sets FUA write support.
- `null_co_parse_filename()` and `null_aio_parse_filename()` accept only `null-co://` or `null-aio://` respectively.
- `null_co_getlength()`, `null_co_preadv()`, `null_co_pwritev()`, and `null_co_flush()` implement coroutine-mode operations.
- `null_aio_preadv()`, `null_aio_pwritev()`, and `null_aio_flush()` implement AIO-mode operations through `NullAIOCB`.
- `null_co_block_status()` reports all requested bytes as offset-valid and optionally zero.
- `null_refresh_filename()` reconstructs exact filenames when only ignorable options are present.
- `bdrv_null_init()` registers both drivers.

## Internal Mechanics
`BDRVNullState` stores virtual length, optional latency, and read-zero behavior. Coroutine operations optionally sleep for `latency-ns` and otherwise complete successfully. AIO operations allocate a `NullAIOCB`; with latency they complete from a realtime timer, otherwise from a replay-safe bottom-half event. Reads fill the destination iovec with zeroes only when `read-zeroes=on`; otherwise read buffers are left untouched.

The block status callback reports a direct mapping to itself and adds `BDRV_BLOCK_ZERO` when configured. Allocated file size is always zero, reflecting that no storage is consumed.

## Dependencies
Uses QEMU block driver APIs, QemuOpts/QDict option parsing, coroutine sleep, AIO callbacks/timers, replay bottom-half scheduling, QEMUIOVector helpers, module registration, and block status flags.

## Risks and Notes
`latency-ns` must be nonnegative. `latency-ns` is deliberately excluded from strong runtime options and ignored when reconstructing an exact filename, while `size` and `read-zeroes` are strong runtime options. The driver supports FUA flags but does not persist anything; it is useful for tests, benchmarking plumbing, and sink-like block nodes rather than durable storage.
