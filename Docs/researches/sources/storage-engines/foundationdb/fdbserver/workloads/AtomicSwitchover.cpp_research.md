# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicSwitchover.cpp

Purpose: defines `AtomicSwitchover`, a two-cluster backup-to-DB workload that exercises `DatabaseBackupAgent::atomicSwitchover()` in both directions. It verifies that source data and prefixed backup data match before switching traffic roles.

Important APIs, types, and functions: `AtomicSwitchoverWorkload` extends `TestWorkload`. Constructor options are `switch1delay`, `switch2delay`, and `stopDelay`; it uses default backup ranges from `addDefaultBackupRanges()`, default backup tag, `backupPrefix`, and a simulated extra database. `_setup()` starts a backup from the extra database into the primary. `diffRanges()` compares source ranges with prefixed destination ranges. `_start()` coordinates wait, diff, switchover, reverse wait, reverse diff, reverse switchover, and abort.

Control flow: client 0 submits a backup from `extraDB` into the primary using `DatabaseBackupAgent`. `_start()` waits until that backup is running, delays randomly up to `switch1delay`, diffs all selected ranges, and calls `atomicSwitchover(extraDB, primary, tag, backupPrefix)`. It then treats the primary as the restore/backup source, waits for backup, delays up to `switch2delay`, diffs in the reverse direction, calls `atomicSwitchover(primary, extraDB, tag, "")`, waits again, delays up to `stopDelay`, and aborts the backup on `extraDB`.

State and persistence behavior: backup-to-DB stores copied keys under `backupPrefix` in the destination database and tracks backup configuration, log ranges, and mutation logs in system keyspaces. `diffRanges()` reads batches of 1000 keys from source and destination, strips the backup prefix from destination keys, and emits mismatch traces for key, value, missing-source, and missing-backup cases.

Dependencies and integration points: uses simulator extra databases, `ClusterConnectionMemoryRecord`, `BackupAgent`, `BulkSetup`, and `fdbSimulationPolicyState().drAgents`. It assumes exactly one extra database and clears DR agents when BackupToDB agents are active at completion.

Risks and edge cases: `diffRanges()` logs mismatches but does not throw directly; simulation severity is the enforcement mechanism. It contains a suspicious combined condition for key-and-value mismatch using `&&` before the separate key/value checks, so the first trace is only emitted when both differ. Check always returns true. Timing is intentionally randomized and can race with backup progress.

Test signals: expected traces progress through `AS_Submit*`, `AS_Wait*`, `AS_Ready*`, `AS_Switch*`, `AS_Abort`, and `AS_Done`; severe traces such as `MismatchKey`, `MismatchValue`, `MissingBkpKey`, and `MissingSrcKey` indicate data divergence.
