# sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.h

Purpose: declares the concrete internal implementation of RocksDB's `ConcurrentTaskLimiter` and the RAII token that releases task reservations.

Important APIs and types: `ConcurrentTaskLimiterImpl` overrides `GetName()`, `SetMaxOutstandingTask()`, `ResetMaxOutstandingTask()`, and `GetOutstandingTask()`, and exposes `GetToken(bool force)` for callers that need to reserve capacity. `TaskLimiterToken` is move-disabled/copy-disabled and holds a raw pointer back to its limiter for release on destruction.

State and lifecycle: the limiter stores `name_`, `max_outstanding_tasks_`, and `outstanding_tasks_`. Tokens increment the outstanding count when created by `GetToken()` and decrement it when destroyed. Copying the limiter is disabled to keep atomics and token back-pointers stable.

Dependencies and integration points: includes public `rocksdb/concurrent_task_limiter.h` and `rocksdb/env.h`. The public factory is declared in the interface header and implemented in the `.cc`, while Java bindings allocate it through JNI.

Risks: the raw pointer in `TaskLimiterToken` makes lifetime ordering explicit but unenforced; users must not destroy the limiter before all tokens. The header's `virtual std::unique_ptr<TaskLimiterToken> GetToken(bool force)` is not part of the public base interface, so code using it must know the concrete type.

Test signals: behavior is expected to be exercised by compaction limiter tests and Java option tests rather than by this header directly.
