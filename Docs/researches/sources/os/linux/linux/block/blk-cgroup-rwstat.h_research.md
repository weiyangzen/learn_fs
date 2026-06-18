# File Research: sources/os/linux/linux/block/blk-cgroup-rwstat.h

## Scope

This private header defines legacy rwstat data structures and inline helpers for block-cgroup policy stats.

## Major Types

- `enum blkg_rwstat_type` tracks `READ`, `WRITE`, `SYNC`, `ASYNC`, and `DISCARD`.
- `struct blkg_rwstat` contains one percpu counter and one auxiliary atomic counter per stat type.
- `struct blkg_rwstat_sample` is a fixed array snapshot of counts.

## Core Helpers

- `blkg_rwstat_add()` classifies an operation by read/write/discard and sync/async, then adds to the relevant counters using `BLKG_STAT_CPU_BATCH`.
- `blkg_rwstat_read()` snapshots percpu counters only.
- `blkg_rwstat_total()` returns read plus write local total.
- `blkg_rwstat_reset()` clears percpu and auxiliary counters.
- `blkg_rwstat_add_aux()` folds another rwstat’s local and auxiliary counts into this rwstat’s auxiliary counters.
- Non-inline functions declared here are implemented in `blk-cgroup-rwstat.c`.

## Dependencies

- `blk-cgroup.h` for `BLKG_STAT_CPU_BATCH`, blkg traversal, and policy data.
- Request operation helpers: `op_is_discard()`, `op_is_write()`, `op_is_sync()`.

## Risks and Invariants

- `blkg_rwstat_add()` assumes external synchronization appropriate to the policy.
- Auxiliary counts are for preserving stats from dead children and should not be confused with current local percpu counts.
- The file is explicitly legacy; adding new users would increase maintenance burden.
