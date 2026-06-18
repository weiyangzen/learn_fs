# sources/storage-engines/rocksdb/db/write_controller.h

Purpose: This header declares `WriteController`, RocksDB's write-stall coordinator for stop, delay, and compaction-pressure states, plus RAII token classes that release pressure when destroyed.

Important APIs/types/functions: `WriteController` exposes `GetStopToken`, `GetDelayToken`, `GetCompactionPressureToken`, `IsStopped`, `NeedsDelay`, `NeedSpeedupCompaction`, `GetDelay`, rate setters/getters, and `low_pri_rate_limiter()`. Token types are `WriteControllerToken`, `StopWriteToken`, `DelayWriteToken`, and `CompactionPressureToken`.

Control flow: Actors such as column families request tokens when write stalls are needed. Active stop tokens make `IsStopped()` true. Active delay tokens make `NeedsDelay()` true and cause writers to call `GetDelay(clock, num_bytes)`. Active compaction-pressure tokens request compaction speedup without necessarily stopping writes. Destructing a token decrements the matching counter.

State and persistence behavior: State is in-memory and process-local: atomic counters for stop/delay/pressure, byte credit and refill timestamp for throttling, max/current delayed write rates, and a low-priority rate limiter. Rate setters clamp zero to one byte/sec and cap current delayed rate at the configured maximum.

Dependencies and integration points: It includes atomics, memory, fixed-width integers, `rocksdb/rate_limiter.h`, and forward declares `SystemClock`. DB mutex discipline is part of the contract. It integrates with write stall conditions from compaction/memtable pressure and low-priority rate limiting.

Risks: Non-atomic delay-credit fields require the documented DB mutex. Token lifetime must be scoped carefully; leaked tokens can permanently stop or delay writes, while premature destruction can remove required backpressure. The default delayed write rate and low-priority limiter values affect write latency under pressure.

Test signals: This item includes implementation but no direct unit test. Expected validation comes from write-stall/compaction-pressure integration tests and destructor assertions.
