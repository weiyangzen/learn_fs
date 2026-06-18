# sources/sync-backup/restic/internal/archiver/scanner_test.go

Purpose: Tests scanner traversal, filtering, error handling, and cancellation.

Important APIs and functions: `TestScanner` checks cumulative `ScanStats` for include-all and `.txt` selection. `TestScannerError` validates no-error, unreadable-directory, and removed-item cases. `TestScannerCancel` verifies graceful early exit after context cancellation.

Control flow and state: Tests build temporary `TestDir` trees, chdir into them, run `NewScanner(fs.Track{FS: fs.NewLocal()})`, collect `Result` callbacks in maps or final counters, and optionally customize `Select`, `Error`, or `Result` to trigger edge cases.

Dependencies and integration: Uses `TestCreateFiles`, `fs.Track`, `internal/test`, `go-cmp`, and OS chmod/remove behavior. Some unreadable-directory coverage is skipped on Windows.

Risks and test signals: The tests guard deterministic sorted traversal, correct aggregation order, filtering of files while preserving directory traversal, ignored filesystem errors, and partial stats after cancellation.
