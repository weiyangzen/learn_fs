<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/restore_progress.go -->
# sources/sync-backup/kopia/cli/restore_progress.go

## Purpose
Provides CLI progress rendering for restore operations, aggregating restore counters and printing throttled stderr status lines with ETA.

## Important APIs, Types, And Functions
Defines `cliRestoreProgress` with atomic counters, throttle, mutex, output writer, and ETA estimator. Methods are `SetCounters`, `Flush`, `maybeOutput`, and `output`.

## Control Flow
Restore code calls `SetCounters` with `restore.Stats`; counters are stored atomically and output is throttled. `output` locks to keep lines monotonic and uses carriage-return rewriting plus padding to erase longer previous lines.

## State And Persistence Behavior
No repository state is changed. State is in-memory progress counters and the last printed line length.

## Dependencies And Integration Points
Integrates `snapshot/restore` stats, `timetrack.Throttle`, ETA estimation, units formatting, and CLI stderr output.

## Risks And Edge Cases
Progress is suppressed until restored size is nonzero, so small metadata-only restores may show little feedback. Atomic counters and mutex protect output, but all callers share the same progress object.

## Test Signals
Tests should validate formatting with skipped/error counts, ETA display, line erasure padding, disabled progress, and flush newline behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/restore_progress.go -->
