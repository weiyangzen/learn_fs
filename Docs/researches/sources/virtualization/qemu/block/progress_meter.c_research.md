# File Research: sources/virtualization/qemu/block/progress_meter.c

## Purpose
Provides small thread-safe helper functions for process progress tracking through QEMU's `ProgressMeter` structure.

## Main Entry Points
- `progress_init()` initializes the progress lock.
- `progress_destroy()` destroys the lock.
- `progress_get_snapshot()` reads `current` and `total` atomically under the lock.
- `progress_work_done()` increments completed work.
- `progress_set_remaining()` sets `total` to `current + remaining`.
- `progress_increase_remaining()` increments `total`.

## Internal Mechanics
All state access is protected by `pm->lock` through `QEMU_LOCK_GUARD`. The helper does not define units; callers decide what `current`, `total`, and increments mean.

## Dependencies
Uses QEMU mutex/lock guard support through coroutine/QEMU headers and the public `qemu/progress_meter.h` declaration.

## Filesystem/Block Relevance
This is support infrastructure for block operations that need progress reporting, such as image conversion, backup, mirror, or similar long-running jobs.

## Risks and Notes
- The helper performs no overflow checks on `current` or `total`.
- It provides snapshots only, not notifications or rate estimation.
