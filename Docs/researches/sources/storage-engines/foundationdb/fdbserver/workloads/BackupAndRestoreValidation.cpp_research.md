# sources/storage-engines/foundationdb/fdbserver/workloads/BackupAndRestoreValidation.cpp

Purpose: defines `BackupAndRestoreValidation`, a compact file-backup workload used to validate that a restore completed and to signal other validation logic through a system-key completion marker.

Important APIs, types, and functions: `restoreValidationCompletionKey` is `"\xff\x02/restoreValidationComplete"`. `BackupAndRestoreValidationWorkload` extends `TestWorkload`; options are `backupAfter`, `restoreAfter`, `backupTag`, and `addPrefix`. `doBackup()` submits and waits for a file backup. `doRestore()` submits a restore, waits for completion, delays for stabilization, writes the completion marker, and unlocks the database. `_start()` coordinates retries.

Control flow: client 0 waits `backupAfter`, runs `doBackup()` into `file://simfdb/backups/`, reads the backup tag metadata to find the container URL, waits until `restoreAfter`, and invokes `doRestore()`. The restore uses `normalKeys` as the restore range, optional `addPrefix`, empty `removePrefix`, and waits for completion. Retryable memory-limit, lock, transaction-too-old, and future-version errors are retried with bounded backoff; other errors are logged as severe and rethrown.

State and persistence behavior: backup metadata is stored through `FileBackupAgent` system keyspaces and backup contents in the file container. The workload writes `restoreValidationCompletionKey` with value `"done"` using `ACCESS_SYSTEM_KEYS` and later unlocks the database with the restore tag. It does not directly compare restored rows.

Dependencies and integration points: includes `ManagementAPI`, `ReadYourWrites`, `BackupAgent`, `BackupContainer`, `SystemData`, `QuietDatabase`, and tester workload definitions. It relies on `makeBackupTag`, `BackupConfig(logUid).backupContainer()`, and standard file-backup restore APIs.

Risks and edge cases: `check()` always returns true, so validation depends on actor completion and the marker being consumed by other workloads or test logic. `restoreAfter - backupAfter` is assumed non-negative in `_start()`. The fixed five-second stabilization delay is a timing heuristic rather than a direct durability proof.

Test signals: progress traces include `BARV_SubmitBackup`, `BARV_BackupComplete`, `BARV_StartRestore`, `BARV_RestoreComplete`, `BARV_RestoreCompletionMarkerSet`, and `BARV_Complete`; retryable failures emit `BARV_RetryableError`.
