# sources/test-tools/fio/io_u.c

## Purpose
Implements fio's I/O unit lifecycle: selecting files, generating offsets and block sizes, enforcing rate and latency targets, preparing `io_u` objects, handling verify/trim backlogs, completing sync and async I/O, updating accounting, filling write buffers, and issuing sync/trim helpers.

## Important APIs, Types, and Functions
Public functions include `__get_io_u`, `get_io_u`, `put_io_u`, `clear_io_u`, `requeue_io_u`, `io_u_quiesce`, `io_u_mark_submit`, `io_u_mark_complete`, `io_u_mark_depth`, `lat_target_init`, `lat_target_reset`, `lat_target_check`, `queue_full`, `io_u_log_error`, `io_u_sync_complete`, `io_u_queued_complete`, `io_u_queued`, `fill_io_buffer`, `io_u_fill_buffer`, `do_io_u_sync`, and `do_io_u_trim`. Internal clusters cover random offset distributions, sequential offsets, zoned modes, mixed read/write direction choice, file service selection, latency target ramping, completion accounting, dedupe/compression buffer generation, and short-I/O requeue.

## Control Flow
`get_io_u()` obtains a free or requeued unit, checks verify and trim backlogs, reads iolog input or selects a file, fills direction/offset/length, updates file positions, fills or scrambles write buffers, sets transfer pointers and priority, then calls `td_io_prep()`. Submission happens through `ioengines.c`. Completion returns through `io_u_sync_complete()` or `io_u_queued_complete()`, which call engine event methods, `io_completed()`, accounting, short-I/O requeue, verify bookkeeping, error handling, bytes-done updates, and `put_io_u()`.

## State and Persistence Behavior
Mutates `thread_data` counters, latency histograms, rate timing, queue-depth state, file positions, random maps, zoned state, verification lists, failed write numberio arrays, bytes done, and per-file write ranges used by sync-file-range. It writes no standalone files, but it drives logs and stats through accounting helpers and determines persistent device/file I/O patterns.

## Dependencies and Integration Points
Tightly integrates with `fio.h`, verify, trim, random generators, axmap, min/max helpers, zoned block devices, data placement, sprandom, ioengine wrappers, logging, stats, file lifetime, iolog replay, and OS trim/sync APIs.

## Risks
This is a high-risk concurrency and correctness file. Offset generation depends on many interacting options: random maps, nonuniform distributions, zone modes, trimwrite/randtrimwrite, time-based loops, and file-service policy. `lat_target_check()` divides by the number of I/Os in a window and assumes progress. Short-I/O requeue mutates buffer pointers and offsets. Parent/child thread accounting and async verify require careful locking. Error paths must avoid double file puts while preserving verification state. Dedupe/compression buffer state is intentionally stateful and can break reproducibility if seeds are changed incorrectly.

## Test Signals
Important signals include fio's random/sequential offset tests, verify and trim backlog jobs, async and sync engine jobs, zoned block device tests, rate limiting tests, latency target tests, short-I/O injection, dedupe/compression buffer reproducibility checks, iolog replay tests, and sanitizer runs under offload/async verify.
