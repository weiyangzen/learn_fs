# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/aggsum.c

## Scope

Implements aggregate-sum counters: fanned-out approximate counters optimized for very frequent updates and comparatively rare precise reads.

Read completely: 233 lines.

## Core Model

An `aggsum_t` has a global core with upper and lower bounds plus per-CPU buckets. Updates usually touch only the current CPU’s bucket. Buckets borrow capacity from the global bounds, allowing local deltas to be adjusted without taking the global lock on every operation.

## Main APIs

- `aggsum_init()` initializes bounds, global lock, bucket array, and per-bucket locks.
- `aggsum_fini()` destroys locks and frees buckets.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` return approximate bounds without locking.
- `aggsum_add()` applies a signed delta to the current CPU bucket, borrowing more range if necessary.
- `aggsum_value()` flushes all buckets to return an exact value.
- `aggsum_compare()` compares the precise value to a target, flushing buckets only until the target is outside the bounds or equality is proven.

## Control Flow

`aggsum_add()` locks one bucket and applies the delta if it fits in the borrowed range. Otherwise it calls `aggsum_borrow()`, which takes the global lock and bucket lock, flushes current bucket state into global bounds, expands the bounds by `abs(delta * aggsum_borrow_multiplier)`, and records the borrowed capacity.

`aggsum_flush_bucket()` folds a bucket’s delta and borrowed range back into the global lower/upper bounds using atomic adds, because bound readers do not take the global lock.

## Dependencies

Uses illumos/ZFS mutexes, atomics, CPU sequence IDs, boot CPU count, kernel memory allocation, and assertion macros.

## Invariants And Risks

- Global bounds may be read locklessly, so updates to bounds use atomic operations.
- Exact reads are intentionally expensive because they flush every bucket.
- `aggsum_compare()` can be cheaper than `aggsum_value()` when bounds prove the comparison before all buckets are flushed.
- Best suited for write-heavy/read-light metrics; frequent exact reads defeat the design.
