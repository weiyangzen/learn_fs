<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/testing.go -->
# sources/sync-backup/restic/internal/restic/testing.go

## Purpose
Provides restic-package helpers intended for tests and fixtures that need deterministic parsing or random IDs.

## Important APIs and Control Flow
`TestParseID` parses an ID string and panics on failure, `TestParseHandle` builds a `BlobHandle` for a parsed ID and blob type, `NewRandomBlobHandle` creates a random data blob handle, and `NewRandomID` fills an `ID` from `crypto/rand`. Control flow is fail-fast: parse or random-reader failures panic so tests can construct fixtures tersely without repetitive error checks.

## State, Persistence, Dependencies, and Integration
State is limited to generated random bytes returned to callers; nothing is persisted. Integration is with tests that need IDs and blob handles without standing up a repository.

## Risks and Test Signals
Risks are panic use outside test contexts and nondeterminism from random IDs. The helper is small and indirectly covered by tests that construct random/mocked repository data.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/testing.go -->
