
# sources/sync-backup/restic/internal/restic/backend_find_test.go

Purpose: tests prefix-based ID lookup.

The test defines sample IDs and a `ListHelper` whose `ListFn` returns those IDs. `TestFind` verifies a unique long prefix returns the expected ID, an invalid prefix returns `NoIDByPrefixError` with a null ID, a prefix longer than any ID is also no-match, and a short prefix matching multiple sample IDs returns `MultipleIDMatchesError` with a null ID.

State is an in-memory slice of IDs. Integration points are `Find`, `Lister`, error types, and ID parsing. Risks covered include accidental partial match behavior for overlong prefixes, returning stale previous matches on error, and failing to distinguish no-match from ambiguity.
