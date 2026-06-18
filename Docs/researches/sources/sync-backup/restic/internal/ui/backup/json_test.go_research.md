<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json_test.go -->
# sources/sync-backup/restic/internal/ui/backup/json_test.go

## Purpose
Tests backup JSON error output.

## Important APIs and Control Flow
`createJSONProgress` builds a `MockTerminal` with verbosity 3. `TestJSONError` and `TestJSONScannerError` verify archival and scan errors are emitted as expected JSON with escaped quotes. Control flow calls printer methods directly and compares captured terminal errors.

## State, Persistence, Dependencies, and Integration
State is mock terminal output. Dependencies include `internal/errors`, `internal/test`, and `ui.MockTerminal`.

## Risks and Test Signals
The tests strongly cover error JSON formatting but do not cover status, verbose item, or summary JSON from this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json_test.go -->
