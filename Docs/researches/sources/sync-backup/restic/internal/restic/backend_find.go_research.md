
# sources/sync-backup/restic/internal/restic/backend_find.go

Purpose: resolves an ID prefix to a unique repository file ID of a given file type.

Important APIs are `Find`, `MultipleIDMatchesError`, and `NoIDByPrefixError`. `Find` creates a cancellable child context, lists all files of the requested type through `Lister`, compares the requested prefix against full hex IDs, records the first match, and errors on a second match. It returns a null ID with either a no-match or multiple-match error when resolution is not unique.

State is read-only; cancellation is local and would allow future optimization but currently only stops through list error propagation. Integration points include key hint lookup, CLI commands resolving snapshots/locks/indexes by prefix, and tests using `ListHelper`. Risks include case sensitivity, prefixes longer than IDs, duplicate prefixes, and backend list errors. Tests in `backend_find_test.go` cover exact unique prefix, no match, too-long prefix, and ambiguous prefix.
