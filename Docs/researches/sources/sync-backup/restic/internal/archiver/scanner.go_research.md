# sources/sync-backup/restic/internal/archiver/scanner.go

Purpose: Implements a lightweight scanner that traverses backup targets and emits cumulative counts for files, directories, other nodes, and bytes without saving data.

Important APIs and types: `Scanner` has `FS`, `SelectByName`, `Select`, `Error`, and `Result` hooks. `NewScanner` installs permissive defaults. `ScanStats` holds counters. `Scan`, `scanTree`, and `scan` drive traversal.

Control flow and state: `Scan` resolves relative targets, builds the same target tree representation as the archiver, and recursively scans leaf nodes. `scan` checks context cancellation, applies name-based selection before `Lstat`, applies metadata-based selection afterward unless the path is explicit, recurses directories in sorted order, updates counters, and calls `Result` after each included item plus once for the final aggregate.

Persistence and dependencies: Scanner is read-only and stores only call-stack counters. It depends on `fs.FS`, sorted directory listing, `debug`, and archiver target-tree helpers.

Integration points: Used by command/UI paths that need pre-backup scan summaries and by selection logic shared with the archiver. Its explicit-target behavior mirrors tree leaf semantics.

Risks and test signals: Risks include divergence from archiver traversal, wrong counts when errors are ignored, and context cancellation returning partial stats. `scanner_test.go` validates include/filter traversal, ignored errors, removed files, and cancellation.
