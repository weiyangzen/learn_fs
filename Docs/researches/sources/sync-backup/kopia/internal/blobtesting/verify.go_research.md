## sources/sync-backup/kopia/internal/blobtesting/verify.go

Purpose: generic blob storage contract verifier and validation option defaults.

Important APIs/types/functions: `VerifyStorage`, `AssertConnectionInfoRoundTrips`, and `TestValidationOptions`.

Control flow, state, and persistence: verifier asserts initial not-found behavior, tolerant delete of missing blobs, concurrent initial puts, full/range reads, list behavior and callback errors, overwrite behavior subject to options, retention extension behavior, deletes/list after deletes, and set/get modification time handling. It mutates the target storage heavily.

Dependencies and integration points: central test suite used by in-memory and real provider tests. Uses `blob`, `gather`, and provider validation defaults.

Risks and test signals: destructive to the target storage namespace, so callers must use isolated test storage. It conditionally treats unsupported set-time as skip and adjusts add concurrency in CI. It encodes the expected provider behavior for many repository components.
