## sources/sync-backup/kopia/internal/blobtesting/faulty.go

Purpose: fault-injection wrapper for `blob.Storage`.

Important APIs/types/functions: method constants, `FaultyStorage`, `NewFaultyStorage`, and wrapped storage methods.

Control flow, state, and persistence: before each supported operation, `GetNextFault` is consulted with method-specific arguments; if a fault is active, the injected error is returned, otherwise the call delegates to the base storage. List item faults can fire inside the callback path.

Dependencies and integration points: used heavily by cache and provider tests to simulate backend/cache failures. Depends on `internal/fault`.

Risks and test signals: retention extension is not fault-injected. Injected faults can alter concurrency timing in tests. Cache tests use it to validate write/read/open failure handling.
