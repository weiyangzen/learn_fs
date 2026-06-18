# sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.cc

Purpose: implements RocksDB's internal `ConcurrentTaskLimiter` used to throttle outstanding tasks such as compaction work while allowing scoped token ownership.

Important APIs and functions: the constructor stores the limiter name, max outstanding task limit, and zero outstanding count. `SetMaxOutstandingTask()` updates the limit, `ResetMaxOutstandingTask()` sets it to `-1` for unlimited, `GetOutstandingTask()` returns the current count, `GetToken(bool force)` tries to reserve a task slot, and `NewConcurrentTaskLimiter()` is the public factory returning the interface pointer. `TaskLimiterToken::~TaskLimiterToken()` releases one outstanding slot.

Control flow: `GetToken()` loads the limit and current task count with relaxed ordering, then loops while forced, unlimited, or below limit. It uses `compare_exchange_weak(tasks, tasks + 1)` so competing threads update `tasks` on failure and retry against the latest value. If the limit is reached and `force` is false, it returns `nullptr`. A successful reservation returns a unique token whose destructor decrements the count.

State and persistence: all state is in atomics on the limiter object and is not persisted. The implementation asserts at destruction that no outstanding task remains, making token lifetime part of object lifetime correctness.

Dependencies and integration points: implements `include/rocksdb/concurrent_task_limiter.h` and is constructed by column-family options, compaction scheduling code, and JNI wrappers. The `force` flag supports bypass paths that must proceed even beyond the configured throttle.

Risks: relaxed atomics are adequate for a counter but provide no ordering for work protected by the limiter. The decrement in `TaskLimiterToken` assumes the limiter outlives all tokens; premature limiter destruction is caught only by debug assertions or undefined behavior. The CAS loop reloads `limit` only once per call, so concurrent limit changes might not affect an in-progress token request until the next call.

Test signals: integration references include DB compaction tests and Java `ConcurrentTaskLimiterTest`. This implementation file has no local unit tests in the subset.
