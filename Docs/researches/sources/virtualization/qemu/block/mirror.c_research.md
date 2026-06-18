# File Research: sources/virtualization/qemu/block/mirror.c

## Purpose
Implements QEMU block mirroring and active commit jobs. It copies data from a source block graph node to a target, tracks concurrent guest writes through a temporary `mirror_top` filter, and completes by either leaving the synchronized target available or replacing a graph node with it.

## Main Entry Points
- `mirror_start()` starts a regular mirror job for `drive-mirror`/blockdev mirror workflows.
- `commit_active_start()` starts active commit by using the same mirror machinery with the base image as target.
- `mirror_start_job()` validates source/target topology, inserts the `mirror_top` filter, creates the dirty bitmap, takes permissions, configures job state, and starts the job.
- `mirror_run()` is the job coroutine: validates sizes, initializes bitmaps/buffers, performs initial dirty discovery/zeroing, runs background copy iterations, transitions to READY, drains, and exits.
- `mirror_iteration()` selects dirty extents, decides copy vs zero vs discard from block status, launches copy operations, and rate-limits progress.
- `mirror_complete()`, `mirror_cancel()`, `mirror_pause()`, `mirror_change()`, and `mirror_query()` implement job lifecycle control.
- `bdrv_mirror_top_*()` implements the temporary filter node’s read/write/zero/discard/flush behavior while the job is active.

## Internal Mechanics
`MirrorBlockJob` owns the target `BlockBackend`, the inserted filter node, source/base references, dirty bitmap, optional COW and zero bitmaps, in-flight bitmap, copy buffers, active-write counters, replacement target, error policies, and copy mode. Copy work is represented by `MirrorOp` objects stored in `ops_in_flight`; conflicting ranges wait on per-operation coroutine queues to preserve ordering.

Background mirroring clears dirty bits before checking block status, records a pseudo-op to block conflicting guest writes, marks chunks in flight, and then issues copy, zero, or discard operations. Read-copy operations use a fixed pool of granularity-sized aligned buffers; completion returns buffers to the free list, updates progress, and wakes waiters. Write failures re-mark ranges dirty and apply the configured block error policy.

The `mirror_top` filter provides consistent reads from the source while intercepting writes. In background copy mode it forwards guest writes to the source and marks the dirty bitmap. In write-blocking mode it prepares an active write op, forwards the write to the source, then synchronously writes the same range to the target, updating dirty/zero bitmaps and progress.

Completion drains the source, waits for all mirror and active writes, flushes the target, optionally adjusts target backing, replaces the selected graph node, removes the filter, unblocks replacement blockers, and restores read-only state for active commit error paths.

## Dependencies
Uses QEMU block job internals, block graph locks and permissions, dirty bitmap APIs, block backend I/O, coroutine queues, QEMU bitmaps, rate limiting, error-action policy, tracepoints, and block graph replacement/drain helpers.

## Risks and Notes
The code is highly concurrency-sensitive: correctness depends on dirty bitmap ordering, in-flight bitmap coverage, pseudo-op wakeups, and graph drain sections matching the current block graph. Active write mode intentionally uses bounce buffers because guest memory may change while the same data must be written to both source and target. Completion can fail late if the requested replacement node no longer has a safe relationship to the source. The dirty bitmap is manually managed by `mirror_top` rather than normal block-layer dirty tracking so the job can switch between background and write-blocking copy modes.
