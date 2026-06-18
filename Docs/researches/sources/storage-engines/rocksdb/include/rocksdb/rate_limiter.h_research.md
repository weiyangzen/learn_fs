# sources/storage-engines/rocksdb/include/rocksdb/rate_limiter.h

Purpose: This header defines RocksDB's IO rate-limiting interface and the factory for the generic token-bucket limiter. It lets DB-wide options throttle reads, writes, or all IO, primarily background flush/compaction but also selected user reads/writes when request options opt in.

Important APIs and types: `RateLimiter` defines `OpType::{kRead,kWrite}` and `Mode::{kReadsOnly,kWritesOnly,kAllIo}`. The constructor defaults to write-only limiting for API compatibility. Virtual APIs include `SetBytesPerSecond()`, optional `SetSingleBurstBytes()`, older `Request(bytes, pri)`, stats-aware `Request(bytes, pri, stats)`, operation-aware `Request(bytes, pri, stats, op_type)`, `RequestToken(bytes, alignment, io_priority, stats, op_type)`, `GetSingleBurstBytes()`, `GetTotalBytesThrough()`, `GetTotalRequests()`, optional `GetTotalPendingRequests()`, `GetBytesPerSecond()`, and `IsRateLimited()`. `NewGenericRateLimiter()` constructs a shareable implementation with rate, refill period, fairness, mode, auto-tuning, and burst size.

Control flow: Callers ask for tokens before IO. The operation-aware `Request()` checks `IsRateLimited(op_type)` and bypasses the limiter for disabled operation types. `RequestToken()` may request a smaller aligned grant than the original byte count, which supports direct IO alignment and burst limits. Implementations block when tokens are unavailable and update statistics when supported.

State and persistence behavior: The limiter holds runtime counters, pending queues, configured rate, burst size, and mode in the implementation. It is not persisted. Sharing one limiter across DB instances coordinates aggregate IO pressure.

Dependencies and integration points: It depends on `Env` for `IOPriority`, `Statistics`, and `Status`. `DBOptions::rate_limiter`, `ReadOptions::rate_limiter_priority`, `WriteOptions::rate_limiter_priority`, flush, compaction, WAL flush, and file readers/writers can use it. Generic limiter fairness distinguishes high- and low-priority requests, commonly flush versus compaction.

Risks and edge cases: Derived classes must not throw exceptions into RocksDB. New implementations should override newer overloads; the deprecated base `Request(bytes, pri)` asserts false. Callers must respect `bytes >= 0` and `bytes <= GetSingleBurstBytes()`. A mode mismatch can unintentionally leave reads or writes unthrottled. Large refill periods can cause bursty stalls; small periods add CPU overhead. `GetTotalPendingRequests()` is optional.

Test signals: Tests should verify mode filtering, dynamic rate changes, burst-size validation, fairness starvation avoidance, stats counters, alignment-aware `RequestToken()`, pending request reporting for the generic limiter, and behavior under concurrent high/low priority load.
