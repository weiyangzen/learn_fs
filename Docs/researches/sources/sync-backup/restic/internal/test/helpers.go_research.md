<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/test/helpers.go -->
# sources/sync-backup/restic/internal/test/helpers.go

## Purpose
Provides shared test assertions, deterministic random data, fixture extraction, temp directory handling, read-only cleanup, and working-directory helpers.

## Important APIs and Control Flow
`Assert`, `OK`, `OKs`, `Equals`, `Random`, `SetupTarTestFixture`, `Env`, `RemoveAll`, `TempDir`, and `Chdir` are widely used by restic tests. Control flow favors fail-fast `testing.TB` helpers, deterministic pseudo-random generation, tar extraction via external `tar`, and cleanup that resets readonly permissions before removal.

## State, Persistence, Dependencies, and Integration
State includes temporary directories, current working directory changes, and environment-derived settings from `vars.go`; no project data is persisted unless cleanup is disabled.

## Risks and Test Signals
Risks are external `tar` dependency, global cwd mutation, and cleanup behavior on Windows readonly files. The helpers are indirectly tested by broad repository test usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/test/helpers.go -->
