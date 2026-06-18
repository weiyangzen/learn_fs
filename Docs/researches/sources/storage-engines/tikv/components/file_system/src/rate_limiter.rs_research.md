<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs -->
# sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs

Purpose: this module implements TiKV's prioritized I/O throughput limiter. It can limit writes, reads, or all I/O, assign priorities per `IoType`, record statistics, and dynamically adjust low-priority budgets.

Important APIs and types: `IoRateLimitMode` supports `WriteOnly`, `ReadOnly`, and `AllIo` and implements serde parsing. `IoRateLimiterStatistics` records read/write bytes per `IoType`. `IoBudgetAdjustor` can adjust low-priority budgets. `IoRateLimiter` exposes `new`, `new_for_test`, `statistics`, `set_io_rate_limit`, `set_io_priority`, `set_low_priority_io_adjustor_if_needed`, sync `request`, async `async_request`, and test-only skewed-clock request. Global `set_io_rate_limiter` and `get_io_rate_limiter` manage the process-wide limiter captured by `File`.

Control flow: `PriorityBasedIoRateLimiter` stores bytes-through and bytes-per-epoch arrays by `IoPriority`, plus protected pending bytes and next refill time. `request_imp!` clamps requests to the current epoch budget, records attempted bytes, returns immediately if within budget or high priority is unrestricted in non-strict mode, otherwise enqueues pending bytes, computes sleep duration, caps any single wait at 500 ms by returning partial quota, records wait metrics, sleeps, and returns granted bytes. `refill` advances epochs, serves pending high/medium bytes first, estimates recent usage, optionally adjusts total budgets before low-priority allocation, and updates per-priority max-byte gauges.

State and persistence behavior: all limiter state is in memory, with atomic counters for hot-path accounting and a mutex for epoch refill/pending queues. Rate limit zero disables flow control. Statistics persist until reset or limiter drop.

Dependencies and integration points: `file.rs` calls `request` while reading/writing, `metrics.rs` records waits and gauges, `MetricsManager` can expose stats, and online config can parse priorities/modes.

Risks: synchronous requests sleep the caller thread, so using the limiter on latency-critical threads requires careful priority config. The algorithm provides best-effort priority isolation, not a hard global cap when high priority can borrow lower-priority budgets in non-strict mode. A single process-global limiter makes test isolation fragile, noted by the "Do NOT use" comment around `set_io_rate_limiter` in test environments.

Test signals: tests cover toggling rate limits, dynamic priority, heavy/light/hybrid flows, approximate throughput, async-compatible logic through the shared macro, and a refill critical-section benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/rate_limiter.rs -->
