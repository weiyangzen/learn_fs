<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress_test.go -->
# sources/sync-backup/restic/internal/ui/restore/progress_test.go

## Purpose
Tests restore progress accounting and printer callbacks.

## Important APIs and Control Flow
Mock printer traces updates, completed items, and errors. Tests cover creation, adding files, first/last progress on a file, completion of the last file, success/error summaries, skipped files, action types including deletion, and error forwarding. Control flow drives `Progress` directly and inspects captured traces after optional `Finish`.

## State, Persistence, Dependencies, and Integration
State is in-memory trace slices and progress maps. Dependencies are restore progress types and shared test helpers.

## Risks and Test Signals
The suite strongly guards aggregate counters and item completion semantics, but timing behavior is intentionally controlled rather than real-time.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress_test.go -->
