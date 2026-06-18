# sources/storage-engines/tikv/components/tikv_util/src/math.rs

## Purpose
Provides a thread-safe moving average for `u32` samples with cheap atomic reads.

## Important APIs, Types, And Functions
`MovingAvgU32Inner` stores a fixed-size circular buffer, current index, and sum. `MovingAvgU32` wraps that inner state in a `Mutex` and exposes a cached `AtomicU32`. Public methods are `new(size)`, `add(sample)`, `fetch()`, and `clear()`.

## Control Flow
`new` fills the buffer with zeros. `add` locks the mutex, advances the circular index, computes the old average, updates the sum by adding the new sample and subtracting the overwritten sample, stores the sample, computes the new average, updates `cached_avg` with relaxed ordering, and returns `(old_avg, new_avg)`. `fetch` reads the cached average without locking. `clear` zeroes the buffer, index, sum, and cached average.

## State And Persistence
All state is in-memory. The mutex protects buffer/sum/index consistency; the atomic cache provides eventually current lock-free reads. There is no persistence.

## Dependencies And Integration
Uses only `std::sync::{Mutex, AtomicU32}`. It can be embedded in metrics, rate smoothing, or adaptive control paths that need low-cost average reads.

## Risks
`new(0)` would create an empty buffer and later `add` would divide/modulo by zero; callers must provide a positive size. Sum is `u32`, so very large windows and samples can overflow in debug or wrap in release. Relaxed ordering is appropriate for approximate metrics but not for synchronization.

## Test Signals
Tests cover monotonic decreasing and increasing sequences with clear/reset behavior, plus random samples checked against an external sum for a partially filled window.
