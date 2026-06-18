# sources/sync-backup/restic/cmd/restic/cmd_restore.go

Purpose: implements `restic restore`, extracting a snapshot or snapshot subfolder to a target directory with filtering, overwrite/delete behavior, sparse restore, verification, and xattr selection.

Important APIs/types/functions: `RestoreOptions`; `runRestore`; `getXattrSelectFilter`.

Control flow and state: collects include/exclude filters, validates one snapshot arg, target presence, mutually exclusive include/exclude and dry-run/verify, and guards `--target / --delete` unless filtered. It opens a read lock, resolves snapshot/latest/subfolder, loads index, creates a `restorer.Restorer`, attaches error/warn/info callbacks, configures file and xattr selection filters, restores to target, finishes progress, returns aggregate errors, and optionally verifies restored files. Repository state is read-only; filesystem target is mutated unless dry-run.

Dependencies and integration points: uses `internal/restorer`, restore UI progress, filter package, snapshot filtering, tree directory resolution, and global JSON mode.

Risks: destructive `--delete` needs the root-target guard. Include/exclude filter semantics affect both traversal and metadata restoration. Verification can surface post-restore errors. JSON mode suppresses info messages.

Test signals: restore integration tests cover include/exclude patterns and files, latest selection, full directory restore, permission errors, metadata on intermediate dirs, and default-layout repos.
