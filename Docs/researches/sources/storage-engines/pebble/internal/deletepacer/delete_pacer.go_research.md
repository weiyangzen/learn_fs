# sources/storage-engines/pebble/internal/deletepacer/delete_pacer.go

## Purpose
This file implements `DeletePacer`, a background queue that rate-limits deletion of obsolete files to reduce disk-performance cliffs while adapting to backlog and low free space.

## Important APIs, Types, And Functions
`DiskFreeSpaceFn` and `DeleteFn` abstract free-space measurement and deletion. `DeletePacer` stores options, logger, queue, pacing bytes, recent history, metrics, condition variable, notify channel, and wait group. `Open`, `Close`, `Enqueue`, `Metrics`, and `WaitForTesting` are the public surface. `queueEntry`, `RecentRateWindow`, and `maxQueueSize` support queue behavior.

## Control Flow
`Open` initializes defaults/history/condition state and starts `mainLoop` under a pprof label. The loop exits only when closed and queue empty, recalculates pacing rate from recent arrivals, backlog, queue bytes, free space, and disabled-pacing flags, waits while in debt, or deletes the next file outside the mutex. `Enqueue` records pacing bytes and history, grows the queue in chunks, updates in-queue metrics, appends entries, and non-blockingly wakes the goroutine. `Close` marks closed, wakes the loop, and waits; pacing is disabled for remaining jobs.

## State And Persistence Behavior
Queue and metrics are in-memory. Deletion side effects are delegated to `DeleteFn` and remove persistent files. Metrics track in-queue and deleted counts/sizes by file type and placement.

## Dependencies And Integration Points
It depends on options/rate calculation and obsolete-file definitions in the same package, `base.Logger`, `metrics.FileCountsAndSizes`, `crtime`, invariants, and pprof labels. Pebble file cleanup code enqueues obsolete table/blob files here.

## Risks And Edge Cases
Risks include queue growth, deletion lag under heavy compaction, low disk space requiring acceleration, enqueue after close, delete function panics or slow deletes, and condition waits. The max queue safety valve disables pacing and logs at most once per minute.

## Test Signals
This subset has no direct delete-pacer tests. Useful signals would include queue metrics, `WaitForTesting`, low-space rate behavior, close draining, and max-queue logging in package tests.
