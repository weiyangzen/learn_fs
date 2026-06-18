## sources/sync-backup/kopia/internal/blobtesting/concurrent.go

Purpose: stress helper for concurrent blob storage access.

Important APIs/types/functions: `ConcurrentAccessOptions` and `VerifyConcurrentAccess`.

Control flow, state, and persistence: generates a pool of random blob IDs, then runs getters, putters, deleters, and listers under an errgroup. Getters accept either valid data with the blob ID prefix or clean not-found errors; deleters accept success or not-found; listers expect no unexpected errors.

Dependencies and integration points: used in provider validation to catch data races and inconsistent error handling. Depends on `blob.Storage`, random data, and `gather.WriteBuffer`.

Risks and test signals: uses package-level `math/rand` concurrently, which may itself be a race concern depending on Go version/API usage. The helper is probabilistic and catches only clean-error contract violations, not strict linearizability.
