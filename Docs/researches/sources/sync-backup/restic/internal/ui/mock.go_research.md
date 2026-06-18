<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/mock.go -->
# sources/sync-backup/restic/internal/ui/mock.go

## Purpose
Provides a test/mock implementation of the UI `Terminal` interface.

## Important APIs and Control Flow
`MockTerminal` records `Print`, `Error`, and `SetStatus` output slices and implements terminal input/output capability methods, password reading, and raw writers. Control flow appends strings to fields or returns fixed terminal capability values suitable for unit tests.

## State, Persistence, Dependencies, and Integration
State is in-memory captured output/errors/status. It integrates with backup/restore JSON/text printer tests.

## Risks and Test Signals
Risks are mock behavior diverging from real terminal status behavior; its test signal comes from widespread use in UI unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/mock.go -->
