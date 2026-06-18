# sources/user-network-fs/rclone/fs/operations/copy_test.go

## Purpose
`copy_test.go` validates single-file copy behavior, partial upload naming, backup/compare/copy destination integration, long filename handling, and transfer-limit enforcement.

## Important APIs, types, and functions
- `TestTruncateString` unit-tests byte truncation with ASCII, multibyte Unicode, emoji, and invalid UTF-8.
- `TestCopyFile` verifies normal copy and no-op self-copy behavior.
- `maxLengthFileName` and `TestCopyLongFile` probe local filesystem filename limits.
- `TestCopyFileBackupDir` validates moving overwritten destination objects into `--backup-dir`.
- `TestCopyFileCompareDest` and `TestCopyFileCopyDest` cover destination avoidance and server-side copy reuse.
- `TestCopyInplace`, `TestCopyLongFileName`, and `TestCopyLongFileNameCollision` exercise partial upload and long-name paths.
- `TestCopyFileMaxTransfer` validates hard, cautious, and soft cutoff behavior.

## Control flow
The tests create `fstest` local/remote files, mutate rclone config via `fs.AddConfig`, call `operations.CopyFile`, and check resulting remote listings. Compare/copy-dest tests create separate destination roots and alternate between stale, matching, and missing files to verify when data is transferred, skipped, copied server-side, or moved to backup. The max-transfer test uses random incompressible data and disables local server-side copies on macOS to force byte accounting.

## State and persistence behavior
All state is temporary test filesystem state. Config values such as `BackupDir`, `CompareDest`, `CopyDest`, `Inplace`, `Transfers`, `MaxTransfer`, and `CutoffMode` are mutated in scoped contexts. Accounting counters are reset around transfer-limit assertions.

## Dependencies and integration points
The file depends on `fs`, `accounting`, `operations`, `sync.CopyDir`, `fstest`, `testify`, crypto randomness, and runtime-specific behavior. It primarily tests `copy.go` but also covers `moveOrCopyFile`, `BackupDir`, `NeedTransfer`, `CompareOrCopyDest`, and partial-upload support from backend feature flags.

## Risks and edge cases
Some scenarios are backend-dependent and skipped when features are missing. Server-side copies can hide byte-transfer accounting, so tests adapt on Darwin/local remotes. Long filename and partial suffix behavior depends on filesystem limits. Copy-dest requires server-side copy support and backup-dir requires server-side move or copy.

## Test signals
The tests confirm copies are idempotent, overwritten files can be preserved in backup dirs, compare-dest can suppress transfers, copy-dest can seed the destination via server-side copy, partial upload names remain safe for long filenames and concurrent collisions, and max-transfer modes return the expected fatal or graceful errors.
