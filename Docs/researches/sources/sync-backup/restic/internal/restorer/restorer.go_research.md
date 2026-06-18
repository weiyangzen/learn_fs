<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer.go -->
# sources/sync-backup/restic/internal/restorer/restorer.go

## Purpose
Coordinates full snapshot restoration: traversal, filtering, overwrite decisions, file-content restore, metadata restore, hardlink recreation, deletion of unexpected files, and verification.

## Important APIs and Control Flow
`Restorer`, `Options`, `OverwriteBehavior`, `NewRestorer`, `traverseTree`, `RestoreTo`, `removeUnexpectedFiles`, `withOverwriteCheck`, `shouldOverwrite`, `VerifyFiles`, and `verifyFile` are the central APIs. `RestoreTo` normalizes the destination, creates the target directory, performs a first tree pass to create directories and collect regular files, delegates file data to `fileRestorer`, then performs a second pass for special nodes, hardlinks, deletion, and metadata. `traverseTreeInner` enforces safe child names and path prefixes, applies select filters, skips sockets, and defers directory metadata until leaving directories. `verifyFile` compares existing/restored files blob-by-blob, optionally trusting mtime for `OverwriteIfChanged`, and feeds partial match state back into incremental restore.

## State, Persistence, Dependencies, and Integration
State includes `fileList` metadata-only flags, options, filters, progress, hardlink index, scratch buffers, and transient verification worker channels. It depends on repository tree/blob APIs, `internal/data`, `internal/fs`, `fileRestorer`, restore UI progress, and errgroup concurrency.

## Risks and Test Signals
High-risk areas are path traversal protection, delete mode, overwrite semantics, metadata-only skips, hardlink handling, partial restore verification, and progress accounting. The large test suite covers basic/relative restore, traversal order, timestamps/permissions, cancellation, sparse files, overwrite modes, dry-run/delete behavior, restore-to-file errors, long paths, Unix hardlinks/permissions, and Windows attributes/case behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer.go -->
