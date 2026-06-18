# sources/storage-engines/rocksdb/util/semaphore.h

## Purpose
Provides RocksDB wrappers for counting and binary semaphores, defaulting to mutex/condition-variable implementations while allowing opt-in use of C++20 standard semaphores.

## Important APIs, Types, And Functions
`CountingSemaphore` exposes `Acquire`, `TryAcquire`, and `Release(n)`. `BinarySemaphore` exposes `Acquire`, `TryAcquire`, and `Release`. When `ROCKSDB_USE_STD_SEMAPHORES` is defined, they wrap `std::counting_semaphore<INT32_MAX>` and `std::binary_semaphore`; otherwise they use `std::mutex`, `std::condition_variable`, and count/state fields.

## Control Flow
Counting acquire waits until `count_ > 0` then decrements. Try-acquire checks and decrements without blocking. Release validates non-negative `n`, increments count, and notifies one waiter for single release or all waiters for multi-release. Binary acquire waits for `state_` true then sets false; release asserts the semaphore is currently unavailable, sets true, and notifies one.

## State And Persistence
State is in-memory semaphore count or boolean state plus synchronization primitives. `CountingSemaphore` is cache-line aligned to reduce false sharing. No persistence exists.

## Dependencies And Integration Points
Depends on standard mutex/condition-variable and optionally `<semaphore>`, plus RocksDB port alignment/cache constants. Used by internal concurrency code needing semaphore semantics without relying by default on buggy standard library semaphore implementations.

## Risks
The default counting implementation can make `Release` briefly wait if another thread is preempted while holding the mutex. Overflow is guarded only by assertions. `BinarySemaphore::Release` asserts precondition in fallback mode to avoid undefined behavior that standard binary semaphores would have for over-release. The standard semaphore path is opt-in because comments document known indefinite-blocking and timeout bugs in implementations.

## Test Signals
No direct assigned test. Expected coverage is indirect through components using these semaphores, especially parallel compression or bounded worker coordination. Dedicated tests should cover blocking wake-up, try-acquire, multi-release notification, over-release assertions in debug, and std/fallback parity.
