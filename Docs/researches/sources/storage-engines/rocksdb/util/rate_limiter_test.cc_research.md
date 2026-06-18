# sources/storage-engines/rocksdb/util/rate_limiter_test.cc

## Purpose
Tests `GenericRateLimiter` behavior across accounting, priority scheduling, timing, dynamic configuration, and historical concurrency bugs.

## Important APIs, Types, And Functions
Test cases include `OverflowRate`, `StartStop`, `GetTotalBytesThrough`, `GetTotalRequests`, `GetTotalPendingRequests`, `Modes`, `GeneratePriorityIterationOrder`, `Rate`, `LimitChangeTest`, `AvailableByteSizeExhaustTest`, `AutoTuneIncreaseWhenFull`, `WaitHangingBug`, and `RuntimeSingleBurstBytesChange`.

## Control Flow
Tests use direct construction and `NewGenericRateLimiter`, invoke `Request` with different `Env::IOPriority` values and op types, spawn writer threads through Env or `std::thread`, and use `SyncPoint` dependencies/callbacks to observe internal states while locks are temporarily released. Mock and special clocks advance refill time deterministically for several tests.

## State And Persistence
State is test-local. The fixture clears sync point callbacks in its destructor to avoid cross-test contamination. No persistent files are written.

## Dependencies And Integration Points
Depends on DB test utilities, mock time env, sync points, RocksDB clock, random generator, and `rate_limiter_impl.h`. It validates integration with statistics in auto-tune tests and with Env thread launching in throughput tests.

## Risks
The `Rate` test is timing-sensitive and explicitly skips minimum-rate assertions under slow CI/valgrind-style environments. Sync-point tests are tightly coupled to internal labels and mutex timing. The coverage is broad but still probabilistic for throughput and fairness behavior.

## Test Signals
The strongest signals are deterministic sync-point checks for pending queues, priority order permutations, limit-change starvation, partial-byte accounting, the wait-hanging regression, and burst-size runtime semantics. Timing tests bound actual throughput to no more than 1.25x target and usually at least 0.80x target.
