<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter_test.go -->
# sources/sync-backup/restic/internal/ui/progress/counter_test.go

## Purpose
Tests the progress counter implementation.

## Important APIs and Control Flow
`TestCounter` creates a counter with a reporting callback, adds values, changes max, and verifies reported value/max/final state after `Done`. Control flow uses short intervals and direct method calls.

## State, Persistence, Dependencies, and Integration
State is local callback-captured progress. Dependencies are the progress package and testing helpers.

## Risks and Test Signals
The test catches basic counter/update behavior but is intentionally light on timing races.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter_test.go -->
