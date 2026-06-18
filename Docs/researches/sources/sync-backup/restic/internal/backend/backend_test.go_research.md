# sources/sync-backup/restic/internal/backend/backend_test.go

Purpose: Tests generic backend unwrapping via `AsBackend`.

Important APIs and types: `testBackend` unwraps to nil; `otherTestBackend` unwraps to its embedded backend. `TestAsBackend` checks direct matches, non-matches, single-level unwrapping, and wrapped non-matches.

Control flow and state: The test constructs small wrapper chains and asserts pointer identity or nil results.

Dependencies and integration: Uses `backend.AsBackend` and `internal/test.Assert`.

Risks and test signals: Guards optional-backend discovery used by higher-level code that needs to recover a concrete backend from wrappers.
