# sources/storage-engines/rocksdb/db/periodic_task_scheduler.h

## Purpose
`periodic_task_scheduler.h` declares the scheduler used by DB instances to manage periodic DB maintenance tasks. It defines the task types, the task function signature, default invalid-period constant, and debug-only inspection hooks.

## Important APIs, Types, And Functions
`PeriodicTaskFunc` is `std::function<void()>`. `kInvalidPeriodSec` is zero and marks disabled/invalid repeat periods. `PeriodicTaskType` enumerates `kDumpStats`, `kPersistStats`, `kFlushInfoLog`, `kRecordSeqnoTime`, `kTriggerCompaction`, and `kMax`.

`PeriodicTaskScheduler` is noncopyable and nonmovable. Public APIs are `Register(task_type, fn, run_immediately)`, `Register(task_type, fn, repeat_period_seconds, run_immediately)`, and `Unregister(task_type)`. Debug builds add `TEST_OverrideTimer`, `TEST_WaitForRun`, `TEST_GetValidTaskNum`, and `TEST_HasTask`.

Private state includes `TaskInfo` with timer task name and period, `tasks_map_`, a pointer to the shared timer returned by `Default`, global task `id_`, and `kMicrosInSecond`.

## Control Flow
Callers register each task type with a callback and period. Re-registering a task type updates the repeat period when it changes, otherwise it is a no-op. Unregister cancels by task type. Debug helpers route to the timer or inspect `tasks_map_`.

## State And Persistence Behavior
The class stores per-scheduler in-memory registration state while using a global timer for execution. It does not own persisted settings; DB options determine which registrations are made. `tasks_map_` is the source of whether a task type is registered for the scheduler instance.

## Dependencies And Integration Points
The header depends on `util/timer.h` and forward-declares `SystemClock`. It is used by `DBImpl` periodic maintenance code and by tests that need deterministic mock-clock scheduling.

## Risks
Because timer state is global but task maps are per instance, all register/unregister operations must stay synchronized with the implementation's global mutex. The debug accessors read `tasks_map_` without local locking in the header, relying on test-controlled access patterns.

`kMax` is used in tests/counts; adding a new enum value requires updating default periods, task names, and expectations.

## Test Signals
Tests check registered task counts, specific task presence, mock-clock waiting, multi-instance aggregate counts, dynamic DB option updates, and trigger-compaction registration periods.
