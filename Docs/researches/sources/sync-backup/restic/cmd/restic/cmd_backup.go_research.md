# sources/sync-backup/restic/cmd/restic/cmd_backup.go

Purpose: implements `restic backup`, creating snapshots from filesystem targets, stdin, or command stdout, with filtering, parent selection, progress reporting, and partial-error semantics.

Important APIs/types/functions: `BackupOptions` holds source, filter, metadata, VSS, stdin, dry-run, and incremental options. `newBackupCommand` registers flags and pre-run defaults for host/read concurrency. `collectTargets`, `readLines`, `readFilenamesRaw`, and `filterExisting` collect source paths. `collectRejectByNameFuncs` and `collectRejectFuncs` assemble archive filters. `findParentSnapshot` locates incremental parents. `runBackup` performs the operation.

Control flow: validates incompatible stdin/password/files-from options, collects existing targets, parses timestamp, opens repository with append lock, loads parent/index, builds target FS including Windows VSS or stdin reader, sets scanner and archiver filters, optionally scans in a goroutine, snapshots with `archiver.New`, reports progress, and returns `ErrInvalidSourceData` when some items failed but a snapshot was created.

State/persistence: creates snapshot, tree, data, index, and lock state in the repository unless `--dry-run`. It may create/delete VSS snapshots and reads local filesystem metadata. Stdin-command execution is external process state.

Dependencies/integration: cobra/pflag, `internal/archiver`, `data`, `fs`, `filter`, `repository`, `restic`, and UI backup progress. Tests and many other commands depend on backup-created repositories.

Risks/test signals: complex option interactions and partial failures are high-risk. Raw filenames require NUL terminators. Parent matching depends on group-by host/path/tags. Tests cover files-from modes, VSS, dry-run, missing files, self-healing, excludes, stdin-command, hardlinks, tags, incremental behavior, and skip-if-unchanged.
