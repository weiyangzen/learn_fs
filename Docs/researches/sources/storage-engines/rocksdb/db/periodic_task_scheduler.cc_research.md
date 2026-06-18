# sources/storage-engines/rocksdb/db/periodic_task_scheduler.cc

## Purpose
`periodic_task_scheduler.cc` implements `PeriodicTaskScheduler`, the DB-owned scheduler for recurring tasks such as stats dumping, stats persistence, info-log flushing, sequence-number time recording, and periodic compaction triggering. It wraps a global single-threaded `Timer` with serialized register/unregister operations and one active task per task type per scheduler.

## Important APIs, Types, And Functions
The file defines global `timer_mutex`, default repeat periods, and short task-name prefixes. `Register` has overloads for default and explicit repeat periods. `Unregister` cancels a task and shuts the timer down if no tasks remain. `Default` returns a static global `Timer` backed by `SystemClock::Default`. Debug builds expose `TEST_OverrideTimer`.

`kDefaultPeriodSeconds` sets `kFlushInfoLog` to 10 seconds and other optional tasks to `kInvalidPeriodSec` until configured explicitly. `kPeriodicTaskTypeNames` supplies readable prefixes for unique timer IDs.

## Control Flow
`Register(task_type, fn, run_immediately)` delegates to the explicit-period overload using the default period. The explicit overload locks `timer_mutex`, rejects period zero, checks for an existing task of the same type, and returns OK without work if the period is unchanged. If the period changed, it cancels and erases the old timer entry.

The scheduler starts the global timer, creates a unique ID from the task prefix and global `id_`, staggers initial delays with an atomic counter modulo the repeat period, and adds the function to the timer. If `run_immediately` is false, it adds a full period to the initial delay. On success it inserts `TaskInfo` into `tasks_map_` and fires a debug sync-point callback with the registered type and period.

`Unregister` locks the same mutex, cancels and erases a registered task if present, and shuts down the timer when it has no pending tasks.

## State And Persistence Behavior
The scheduler has only in-memory state. Per-instance `tasks_map_` tracks the task name and repeat period for each task type. The global timer and global ID are process-level state shared by DB instances. No task registration survives DB process restart; DB open/options code must re-register tasks.

Initial delay staggering spreads tasks registered by different DBs or task types over the period to reduce synchronized wakeups. Info-log flushing is expected to keep the timer available even when other periodic tasks are disabled.

## Dependencies And Integration Points
The implementation depends on `util/timer.h`, `rocksdb/system_clock.h`, `port::Mutex`, `MutexLock`, and SyncPoint in debug builds. It integrates with DBImpl startup/options code that registers/unregisters periodic work and with tests that override the timer clock.

## Risks
The global mutex is intentionally coarse because `Timer::Start`, `Shutdown`, `Add`, and `Cancel` are not independently thread-safe. Any new caller bypassing this mutex could race global timer state or `tasks_map_`.

Registering a task with the same period does not update the callback function. This is part of the current semantics but can surprise callers expecting function replacement. The initial-delay modulo uses `repeat_period_seconds`; period zero is rejected before modulo to avoid division by zero.

Global timer sharing means multi-DB behavior depends on correct unique IDs and cancellation by stored name. A leaked task would keep the timer running after DB close.

## Test Signals
`periodic_task_scheduler_test.cc` checks task firing under a mock clock, dynamic unregister/re-register through DB options, trigger-compaction period registration, multiple DB instances sharing the global timer, and multiple Env wrappers with the same clock.
