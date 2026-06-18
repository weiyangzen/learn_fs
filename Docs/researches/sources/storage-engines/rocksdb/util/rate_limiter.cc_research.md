# sources/storage-engines/rocksdb/util/rate_limiter.cc

## Purpose
Implements RocksDB's generic token-bucket-style rate limiter for reads and writes with priority queues, fairness randomization, dynamic rate updates, optional auto tuning, and cooperative sleeping/refilling by requester threads.

## Important APIs, Types, And Functions
`RateLimiter::RequestToken` clamps requests to burst size, aligns direct I/O requests, and delegates to `Request`. `GenericRateLimiter::Request` is the main blocking token request path. `SetBytesPerSecond`, `SetSingleBurstBytes`, `GeneratePriorityIterationOrderLocked`, `RefillBytesAndGrantRequestsLocked`, `CalculateRefillBytesPerPeriodLocked`, `TuneLocked`, and `NewGenericRateLimiter` implement configuration, scheduling, accounting, and factory behavior. Internal `Req` tracks original bytes, remaining bytes, and a condition variable.

## Control Flow
Requests first consume `available_bytes_` if present, then enqueue a stack-local `Req` in the priority queue. Queued requester threads coordinate under `request_mutex_`: one waits until `next_refill_us_`, while another performs refill and grants queued requests. Refill resets `available_bytes_`, generates a priority iteration order with `IO_USER` first and randomized fairness among high/mid/low, then grants full or partial requests from queue fronts. Destruction sets `stop_`, signals queued requests, and waits for each blocked request to exit.

## State And Persistence
All limiter state is in memory: atomics for rate, refill bytes, and burst size; counters for requests and bytes-through; queues per `Env::IOPriority`; refill timing; fairness RNG; auto-tune counters; and the injected `SystemClock`. There is no persistence. Accounting totals are guarded by `request_mutex_`.

## Dependencies And Integration Points
Depends on `rocksdb/rate_limiter.h`, `rocksdb/env.h`, `rocksdb/system_clock.h`, `monitoring/statistics_impl.h`, `test_util/sync_point.h`, `util/mutexlock.h`, and `util/random.h`. It integrates with RocksDB Env I/O code through `RateLimiter`, with statistics through `RecordTick(NUMBER_RATE_LIMITER_DRAINS)`, and with tests through sync points and injectable clocks.

## Risks
Correctness depends on every queued `Req` being stack-live while queued and removed before return. Sleep/refill coordination is subtle; missed signals can hang requests. Dynamic rate reductions can make queued requests larger than refill size, so partial grants are required. `RequestToken` may request at least one alignment unit even above burst for direct I/O. Auto tuning uses drain percentage heuristics and can oscillate or underutilize if workload signals are misleading. Destructor wake-up must not race with incoming requests.

## Test Signals
`rate_limiter_test.cc` covers start/stop, overflow-safe refill calculation, total bytes/requests accounting, pending request accounting via sync points, mode filtering, priority iteration order, approximate rate limiting under concurrency, dynamic limit changes, partial available-byte exhaustion, auto tuning increase/decrease, a historical wait-hanging bug, and runtime single-burst changes.
