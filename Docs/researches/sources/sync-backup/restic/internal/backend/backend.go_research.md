# sources/sync-backup/restic/internal/backend/backend.go

Purpose: Defines the central backend abstraction used by restic repositories and wrapper layers.

Important APIs and types: `ErrNoRepository`, `Backend`, `Properties`, `Unwrapper`, `AsBackend`, `FreezeBackend`, `FileInfo`, and `ApplyEnvironmenter`. The interface includes save/load/stat/list/remove/delete/close, hashing, not-exist/permanent-error classification, and warmup methods.

Control flow and state: This file has no persistence. The key logic is `AsBackend`, which walks wrapper chains via `Unwrap` until it finds a backend of the requested generic type or returns the zero value.

Dependencies and integration: All concrete backend packages implement this interface. Retry logic relies on permanent error classification; cache/dryrun/limiter/sema/retry wrappers rely on interface composition and optional unwrapping.

Risks and test signals: Interface contract drift affects all storage backends. `Load` requires idempotent callbacks because retry wrappers may call them multiple times. `backend_test.go` validates `AsBackend` through wrapper chains.
