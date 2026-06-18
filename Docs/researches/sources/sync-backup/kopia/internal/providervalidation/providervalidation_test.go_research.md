# sources/sync-backup/kopia/internal/providervalidation/providervalidation_test.go

Purpose: smoke-tests provider validation against in-memory storage.

Important APIs/types/functions: `TestProviderValidation`, `blobtesting.NewMapStorage`, and `DefaultOptions` with shortened duration.

Control flow: constructs a map storage, adjusts validation options to make the run cheap, and asserts `ValidateProvider` succeeds.

State and persistence behavior: temporary validation blobs live only in map storage and should be cleaned up.

Dependencies and integration points: confirms the validation path works for a compliant provider.

Risks and test signals: this is a happy-path test; additional tests should inject bad metadata, wrong missing errors, failed partial reads, and clock drift.
