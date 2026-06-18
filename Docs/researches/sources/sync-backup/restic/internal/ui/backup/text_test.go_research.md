<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text_test.go -->
# sources/sync-backup/restic/internal/ui/backup/text_test.go

## Purpose
Tests text backup error output.

## Important APIs and Control Flow
`createTextProgress` builds a text printer backed by `MockTerminal`. `TestError` and `TestScannerError` verify archival and scan errors are printed in the expected human-readable form. Control flow calls printer methods directly and compares captured mock output.

## State, Persistence, Dependencies, and Integration
State is mock terminal output. Dependencies are shared test helpers and `internal/errors`.

## Risks and Test Signals
Coverage is focused on error text; full status and summary formatting is mainly exercised indirectly and through common UI format tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text_test.go -->
