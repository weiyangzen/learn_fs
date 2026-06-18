# sources/storage-engines/foundationdb/fdbserver/workloads/BackupToDBAbort.cpp

Purpose: defines `BackupToDBAbort`, a small backup-to-DB workload that starts a DR backup, waits, locks the primary database, aborts the backup, unlocks the backup state, and later unlocks the database. It focuses on abort/lock cleanup behavior.

Important APIs, types, and functions: `BackupToDBAbort` extends `TestWorkload`; the main option is `abortDelay`. `_setup()` submits a default-tag backup from the simulated extra database to the primary with default backup ranges and a fixed backup prefix. `_start()` performs the timed abort sequence. `check()` unlocks the database and returns true. It registers through `WorkloadFactory<BackupToDBAbort>`.

Control flow: only client 0 runs. Setup creates `extraDB`, instantiates `DatabaseBackupAgent`, submits backup with `StopWhenDone::False`, and tolerates duplicate backup errors. Start waits `abortDelay`, waits for the backup to be active, generates a lock UID, locks the primary database, aborts the backup on `extraDB`, unlocks the backup tag, and completes. Check releases the primary database lock.

State and persistence behavior: DR backup metadata and copied data are stored by `DatabaseBackupAgent` in the participating databases. The workload stores only an in-memory `UID lockid` but persists the database lock until `check()`. It does not compare copied data or inspect leftover metadata.

Dependencies and integration points: depends on `BackupAgent`, `ManagementAPI`, `NativeAPI.actor.h`, tester workload definitions, simulator extra databases, `lockDatabase`, `unlockDatabase`, and `unlockBackup`. It assumes one configured extra database.

Risks and edge cases: if `_start()` fails after locking but before `check()`, the database can remain locked until simulation teardown or another cleanup path. `check()` always returns true after unlocking and does not validate backup-agent state. The workload is intentionally narrow and should be paired with broader correctness tests.

Test signals: actor completion without unexpected exceptions is the primary signal; duplicate backup is tolerated, while other backup submission errors fail setup.
