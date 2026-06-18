<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/password.go -->
# sources/sync-backup/restic/internal/terminal/password.go

## Purpose
Implements terminal password reading support.

## Important APIs and Control Flow
The file provides password prompt/read helpers that use raw terminal input where possible and respect context cancellation. Control flow prompts on the terminal, reads without echo through terminal APIs, and returns password text or errors.

## State, Persistence, Dependencies, and Integration
State is transient terminal mode/input data; no password is persisted. Integration is with the `Terminal` abstraction used by commands needing repository passwords.

## Risks and Test Signals
Risks are echo leakage, hanging reads under cancellation, and non-terminal input behavior. Tests for terminal abstractions and UI mocks provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/password.go -->
