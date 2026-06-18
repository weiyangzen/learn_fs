<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text_test.go -->
# sources/sync-backup/restic/internal/ui/restore/text_test.go

## Purpose
Tests restore text progress output.

## Important APIs and Control Flow
The tests use `MockTerminal` and assert exact output for status updates, skipped counters, success/error summaries, skipped summaries, complete-item action strings, and restore errors. Control flow calls text printer methods directly with representative state and actions.

## State, Persistence, Dependencies, and Integration
State is captured mock terminal output/errors. Dependencies are shared test helpers and UI mocks.

## Risks and Test Signals
Coverage is strong for current text contracts; real terminal width/status behavior is covered indirectly by terminal/progress code.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text_test.go -->
