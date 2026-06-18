# sources/storage-engines/rocksdb/util/rate_limiter_impl.h

## Purpose
Declares `GenericRateLimiter`, the concrete implementation behind RocksDB's public `RateLimiter` factory.

## Important APIs, Types, And Functions
The class overrides `SetBytesPerSecond`, `SetSingleBurstBytes`, `Request`, `GetSingleBurstBytes`, `GetTotalBytesThrough`, `GetTotalRequests`, `GetTotalPendingRequests`, and `GetBytesPerSecond`. `TEST_SetClock` allows tests to replace the clock. Private helpers handle refill/grant, priority ordering, refill-byte calculation, auto tuning, and locked rate updates.

## Control Flow
Public methods acquire `request_mutex_` for shared state except atomic getters. `GetSingleBurstBytes` returns explicit burst size or current refill bytes when raw burst is zero. Aggregate getters sum arrays over all priorities when passed `Env::IO_TOTAL`. `NowMicrosMonotonicLocked` derives monotonic microseconds from the current clock's nanosecond source.

## State And Persistence
The class stores the refill period, atomics for rate/refill/burst, a mutable clock, stop flag, condition variable for destructor exit, per-priority totals and queues, available bytes, next refill time, fairness RNG, wait/refill coordination flag, and auto-tune state. No durable state exists.

## Dependencies And Integration Points
Includes RocksDB Env, RateLimiter, Status, SystemClock, `util/mutexlock.h`, and `util/random.h`. It is included by `rate_limiter.cc` and tests needing direct construction or clock injection.

## Risks
The header exposes many implementation details to tests but not to public API consumers. Atomic values are relaxed because the mutex protects operational state; incorrect future reads outside the mutex could observe stale values. Priority arrays are indexed by `Env::IOPriority` enum values and depend on enum layout. Queue entries are raw pointers to stack objects owned by blocked request calls.

## Test Signals
The direct-construction tests in `rate_limiter_test.cc` validate getters, dynamic setters, pending queue reporting, test clock injection, and behavior under edge conditions such as overflow and custom burst sizing.
