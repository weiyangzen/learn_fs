# sources/storage-engines/foundationdb/fdbbackup/backup.cpp

## Purpose

`backup.cpp` is the multi-binary command implementation behind `backup_agent`, `fdbbackup`, `fdbrestore`, `dr_agent`, and `fdbdr`. It owns top-level CLI option tables, help output, executable-name dispatch, argument normalization, network/client setup, backup-agent status publication, and command-to-actor routing. It does not implement the core backup algorithms itself; instead it validates and translates CLI state into calls on `FileBackupAgent`, `DatabaseBackupAgent`, `IBackupContainer`, `BackupConfig`, and bulk backup/restore metadata APIs.

## Important APIs, Types, and Functions

Important local enums are `ProgramExe`, `BackupType`, `DBType`, and `RestoreType`, which classify the executable and subcommand. `getSnapshotMode`, `getRestoreMode`, and `getMutationLogType` map user strings to `SnapshotMode`, `RestoreMode`, and `MutationLogType`. The large `CSimpleOpt::SOption` arrays define supported flags for each action, including snapshot mode (`rangefile`, `bulkdump`, `both`), restore mode (`rangefile`, `bulkload`), blob credentials, encryption key and block size, tag names, key ranges, and DR source/destination clusters.

The main operational wrappers are `runAgent`, `runDBAgent`, `submitBackup`, `submitDBBackup`, `switchDBBackup`, `statusBackup`, `statusDBBackup`, `abortBackup`, `abortDBBackup`, `waitBackup`, `discontinueBackup`, `changeBackupResumed`, `changeDBBackupResumed`, `runRestore`, `dumpBackupData`, `expireBackupData`, `deleteBackupContainer`, `describeBackup`, `queryBackup`, `listBackup`, `listBackupTags`, and `modifyBackup`. `openBackupContainer` centralizes backup URL validation and container construction. `parseLine`, `addKeyRange`, and `decode_hex_string` integration parse user key ranges and restore prefixes.

`getLayerStatus`, `cleanupStatus`, `statusUpdateActor`, and `updateAgentPollRate` are the embedded layer-status subsystem for backup and DR agents. They build expiring JSON status documents and adjust per-agent polling based on aggregate process count.

## Control Flow

Startup calls `platformInit`, registers crash handling, normalizes stdout/stderr buffering, derives `ProgramExe` from `argv[0]`, then calls `reorderArguments`. `reorderArguments` moves non-option positional arguments before options so commands can be supplied before or after flags while still feeding `CSimpleOpt` a predictable command-first argv. `processOption` validates options against all option tables, including prefix options such as `--knob-`, accepts `--opt=value`, and treats dash/underscore spellings as equivalent.

After option parsing, `main` accumulates CLI state in local variables, configures trace logging, TLS, blob credentials, memory limits, client knobs, default backup ranges, and optional user/system restore ranges. It then initializes the network and selects one actor future by executable and subcommand. Most `fdbbackup` actions require a destination cluster via `initCluster`, while container-only actions such as list/delete/describe/dump/expire may only open trace files and containers. `fdbrestore` requires an explicit destination cluster file unless running dry-run validation. DR commands initialize both source and destination clusters, with abort optionally allowing destination-only behavior.

The selected actor is wrapped in `stopAfter`, `runNetwork` drives it, and exit status is derived from future completion. Errors are reported through `TraceEvent`, stderr messages, and FoundationDB exit codes.

## State and Persistence Behavior

The command mutates several persistent stores. Backup and restore lifecycle operations write FoundationDB system keyspace metadata through `FileBackupAgent` and `DatabaseBackupAgent`, including backup tags, state enums, mutation-stream IDs, pause keys, snapshot intervals, target snapshot versions, backup container metadata, and restore requests. `modifyBackup` performs transactionally guarded mutations to existing `BackupConfig` records, verifying the tag, aborted flag, runnable state, optional UID, new container, encryption metadata, and snapshot interval fields before commit.

Agent status is persisted under layer status key ranges. Status documents use JSON operators such as `$expires`, `$sum`, `$max`, and `$latest`, so dead agents age out without explicit cleanup. The status payload includes process information, locality, blob I/O stats, backup tag state, restorable version lag, byte counters, mutation stream IDs, pause state, and encryption key setup status.

Container operations persist to external backup stores through `IBackupContainer`: create/open, describe, list, expire, delete, dump file lists, get restore sets, and write encryption metadata. Blob credentials are loaded from CLI files and environment; proxy settings may come from `HTTP_PROXY` or `HTTPS_PROXY`.

## Dependencies and Integration Points

The file integrates FoundationDB Flow actors/coroutines, client APIs, `BackupAgent.h`, `BackupContainer.h`, `ManagementAPI.h`, `BulkLoading.h`, TLS and blob credential setup, JSON status builders, `SimpleOpt`, and platform-specific parent PID watching on Windows. Newer BulkDump/BulkLoad behavior is exposed through `SnapshotMode` and `RestoreMode`, but actual data movement is delegated below the CLI layer. `AuditStorageCommand.cpp` and the shell tests rely on restore-prefix behavior and backup status output from this file.

## Risks and Edge Cases

Argument reordering is broad: it validates against all option arrays before the specific subcommand parser runs, so an option valid for one command can be reordered and then rejected later by the selected `CSimpleOpt` table. This improves flexible command positioning but makes option-table drift risky. `BackupModifyOptions::hasChanges` ignores `encryptionKeyFile` unless a destination URL or interval is also present, matching the later warning that key-only changes do not apply, but it may surprise users. `openBackupContainer` blocks `../` substrings but delegates full URL validation to container implementations. BulkDump snapshot generation is asynchronous from backup submission, so status becoming restorable does not necessarily mean all BulkDump metadata is already visible.

Restore validation rejects simultaneous target version and timestamp, requires an original cluster file to resolve timestamps, and supports incremental-only mutation-log restore into non-empty destinations. Encryption requires a key file before a positive block size can be accepted. BulkLoad restore mode is passed as a boolean choice to `FileBackupAgent::restore`; missing or incomplete BulkDump datasets are expected to surface below this layer.

## Test Signals

The `EXCLUDE_MAIN_FUNCTION` block includes parser tests for command reordering, `--opt=value`, missing parameters, prefix knob options, option-as-parameter behavior, and query command cluster-file support. The shell tests in this work item exercise local and blob backup/restore, encryption mismatch failures, partitioned mutation logs, BulkDump snapshot mode `both`, BulkLoad restore mode, and status JSON.
