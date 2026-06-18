# sources/storage-engines/rocksdb/util/thread_list_test.cc

## Purpose

Tests thread status global tables and runtime thread-list reporting when background tasks set column-family, operation, and state metadata.

## APIs, control flow, and state

`SimulatedBackgroundTask` registers column-family info, marks current background threads with tracking, operation, and state, waits until signaled to finish, then clears thread status state. `GlobalTables` verifies operation/state/stage arrays are indexed exactly by enum values and names match `ThreadStatus` helpers. `SimpleColumnFamilyInfoTest` schedules high/low priority work, reserves idle threads, inspects `Env::GetThreadList`, and releases reservations. `SimpleEventTest` schedules flush and compaction tasks, terminates groups incrementally, and verifies collected operation counts update.

## Dependencies and integration

The test depends on `monitoring/thread_status_updater.h`, `rocksdb/db.h`, Env background scheduling, and global tables declared in `thread_operation.h`. It is disabled into a no-op binary when `NROCKSDB_THREAD_STATUS` is defined.

## Risks and test signals

Signals cover table enum drift, thread tracking registration, column-family attribution, priority classification, reservation behavior, and clearing status after task completion. The tests depend on scheduler timing but use condition variables to wait for running counts.
