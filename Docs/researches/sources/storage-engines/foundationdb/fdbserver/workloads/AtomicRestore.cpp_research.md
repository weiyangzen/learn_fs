# sources/storage-engines/foundationdb/fdbserver/workloads/AtomicRestore.cpp

Purpose: defines `AtomicRestore`, a simulation workload that starts a file backup and then repeatedly attempts an atomic restore from that backup while other activity may continue. It is a minimal smoke/stress workload for the `FileBackupAgent::atomicRestore()` path.

Important APIs, types, and functions: `AtomicRestoreWorkload` extends `TestWorkload`. Constructor options include `startAfter`, `restoreAfter`, `backupRanges`, `mutationLogType`, `addPrefix`, and `removePrefix`. `hasPrefix()` detects prefix remapping mode. `_start()` performs the entire workload. The workload registers through `WorkloadFactory<AtomicRestoreWorkload>`.

Control flow: only client 0 runs. `_start()` waits for a randomized fraction of `startAfter`, submits a backup to `file://simfdb/backups/` with default tag, waits for the backup to become active, waits a randomized fraction of `restoreAfter`, and then loops calling `backupAgent.atomicRestore()` with the backup URL, selected ranges, mutation log type, and prefix arguments. Duplicate or unneeded backup errors are tolerated; other errors propagate. After a successful restore, file-backup simulations call `fdbbackupAgents.clear()` to quiesce backup agents.

State and persistence behavior: backup metadata and mutation logs are written by the file backup agent under the normal backup system keyspaces, and backup data is stored in the simulation file container. The workload does not verify restored contents directly; persistent state is managed by `FileBackupAgent`. Prefix remapping is constrained by assertions: both prefixes must be empty in current construction, and `removePrefix` must be empty.

Dependencies and integration points: includes `ManagementAPI`, `BackupAgent`, `BackupContainerFileSystem`, simulator policy state, knobs, tester workload definitions, and `BulkSetup` for range parsing. It exercises backup-agent global state and is sensitive to `FDBBackupAgentType::BackupToFile`.

Risks and edge cases: `check()` always returns true, so failures surface only as thrown actor errors or severe traces from lower layers. The restore loop retries indefinitely on accepted duplicate/unneeded conditions with a fast-spin delay, which can mask a stuck precondition until simulation timeout. Prefix-remap assertions show the workload is not currently a broad prefix-restore validator.

Test signals: successful completion logs `AtomicRestore_Start`, `AtomicRestore_BackupStart`, `AtomicRestore_RestoreStart`, and `AtomicRestore_Done`; unexpected backup or restore exceptions fail the simulation actor.
