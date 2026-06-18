# sources/storage-engines/rocksdb/db/periodic_task_scheduler_test.cc

## Purpose
`periodic_task_scheduler_test.cc` verifies periodic DB task scheduling with deterministic mock time and selected real-time integration. It covers basic task firing, dynamic DB option changes, periodic compaction trigger period computation, time-based column-family selection, multiple DB instances sharing the global timer, and multiple Env wrappers.

## Important APIs, Types, And Functions
`PeriodicTaskSchedulerTest` extends `DBTestBase`, installs a `MockSystemClock` through a `CompositeEnvWrapper`, and uses a sync point (`DBImpl::StartPeriodicTaskScheduler:Init`) to call `PeriodicTaskScheduler::TEST_OverrideTimer`.

`TriggerCompactionTest` is a separate `DBTestBase` fixture that avoids mock-clock interactions for multi-CF trigger-compaction selection.

The tests use DB options such as `stats_dump_period_sec`, `stats_persist_period_sec`, `periodic_compaction_seconds`, `ttl`, `bottommost_file_compaction_delay`, FIFO file-temperature thresholds, `max_compaction_trigger_wakeup_seconds`, and `read_triggered_compaction_threshold`. They observe sync points in `DumpStats`, `PersistStats`, `FlushInfoLog`, `TriggerPeriodicCompaction`, and scheduler registration.

## Control Flow
`Basic` opens a DB with dump/persist periods, counts periodic callback invocations under mock sleeps, disables dump/persist through `SetDBOptions`, verifies info-log flush keeps running, re-enables dump stats with a new period, and checks trigger compaction fires after its non-immediate period.

`TriggerCompactionPeriodComputation` captures the period used when registering `kTriggerCompaction`. It opens/reopens DBs under many option combinations: 12-hour cap from long stats dump, stats dump/persist periods, periodic compaction divided by the trigger divisor, TTL, bottommost delay, FIFO file-temperature thresholds, minimum across multiple column families, clamping to 1 second, and `max_compaction_trigger_wakeup_seconds` caps.

`QueuesAllTimeBasedOptions` creates multiple column families with different compaction-related options and waits for periodic compaction. A sync point records which CFs have compaction scores computed. CFs with periodic, TTL, bottommost, FIFO temperature, or read-triggered options should be considered; default and explicitly none should not.

`MultiInstances` opens ten DBs with the same mock Env, verifies aggregate pending task counts, advances mock time to count callbacks across instances, closes half the DBs, and verifies only remaining instances fire. `MultiEnv` opens DBs through different Env wrappers sharing the mock clock to ensure scheduler/timer use is compatible.

## State And Persistence Behavior
The scheduler state is in-memory and tied to DB lifetime/options. These tests verify that DB option updates mutate registered tasks without reopening and that closing DB instances unregisters their tasks. Multi-CF tests persist CF descriptors and reopen with distinct options to validate trigger-period computation across stored/opened column families.

Periodic compaction selection is not testing compaction output; it tests that configured CFs enter the scoring path when the periodic trigger fires.

## Dependencies And Integration Points
The file depends on `db/periodic_task_scheduler.h`, `db/column_family.h`, `db/db_test_util.h`, `env/composite_env_wrapper.h`, and `test_util/mock_time_env.h`.

Integration points include DBImpl scheduler startup, DB option mutation, ColumnFamilyData iteration, trigger-compaction period computation, FIFO compaction options, mock clock timed waits, SyncPoint, and global timer sharing.

## Risks
Mock-clock scheduling can be sensitive to timer wait points, so the fixture installs `InstallTimedWaitFixCallback` and uses `TEST_WaitForPeriodicTaskRun`. Trigger compaction uses `run_immediately=false`, so tests account for elapsed mock time carefully.

Global timer sharing means tests can interfere if callbacks/sync points are not cleared by fixture teardown; these tests rely on DBTestBase and SyncPoint handling. The period-computation test destroys/reopens DBs repeatedly to avoid persisted CF/options leakage.

## Test Signals
Success signals include exact callback counters after mock sleeps, expected pending task counts, scheduler changes after `SetDBOptions`, captured trigger-compaction periods for 13 option cases, CF names observed or not observed during trigger scoring, aggregate callback counts across ten DB instances, and clean close across multiple Env wrappers.
