<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json_test.go -->
# sources/sync-backup/restic/internal/ui/restore/json_test.go

## Purpose
Tests restore JSON progress output.

## Important APIs and Control Flow
The tests build a `MockTerminal` JSON printer and assert exact JSON strings for status updates, skipped counters, successful/error summaries, verbose complete-item actions, and error output. Control flow calls printer methods directly with representative `State` values and item actions.

## State, Persistence, Dependencies, and Integration
State is captured mock terminal output and errors. Dependencies are shared test helpers and UI mocks.

## Risks and Test Signals
Coverage is strong for output contract stability, though exact floating-point percent text remains part of the contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json_test.go -->
