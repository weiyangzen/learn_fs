# sources/storage-engines/rocksdb/db/write_callback.h

Purpose: This header defines the internal `WriteCallback` interface used by DB write paths to run caller-provided validation or side effects on the write thread before a write executes.

Important APIs/types/functions: `WriteCallback` has a virtual destructor, pure virtual `Status Callback(DB* db)`, and pure virtual `bool AllowWriteBatching()`. `DB` is forward-declared to avoid including the full DB interface.

Control flow: DB write code attaches a callback to a `WriteThread::Writer`. Before execution, the write thread invokes `Callback`; a non-OK status aborts that writer's write and is returned to the caller. `AllowWriteBatching()` tells write-thread grouping whether this callback can be batched with other writes.

State and persistence behavior: The interface owns no state. Implementations may hold state such as "was called" flags or validation options. A failing callback prevents WAL/memtable persistence for that write.

Dependencies and integration points: It depends on `rocksdb/status.h` and integrates with `DBImpl::WriteWithCallback`, `WriteThread::Writer`, write grouping, background error reporting for callback failures, and tests in `write_callback_test.cc`.

Risks: Callbacks run on the write path, so expensive or blocking implementations can stall writers. Returning incorrect batching permission can break ordering assumptions or reduce throughput. Callback implementations must tolerate being invoked under write-thread synchronization constraints.

Test signals: `write_callback_test.cc` verifies callback invocation, abort semantics, batching policy behavior across write configurations, and interaction with `UserWriteCallback`.
