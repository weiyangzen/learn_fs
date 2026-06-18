# sources/sync-backup/restic/cmd/restic/cmd_check.go

Purpose: implements `restic check`, validating repository indexes, packs, snapshots, tree/blob structure, and optional data contents.

Important APIs/types/functions: `CheckOptions` controls `--read-data`, `--read-data-subset`, `--with-cache`, and snapshot filters. `checkFlags`, `stringToIntSlice`, and `parsePercentage` validate subset syntax. `prepareCheckCache` configures temporary or existing caches. `runCheck` executes the checker. `buildPacksFilter` selects all, bucket, percentage, or size-based pack subsets. `checkSummary` and `jsonErrorPrinter` support JSON output.

Control flow: validates flags, prepares cache, opens exclusive lock, loads filtered snapshots/indexes, reports index hints/errors, checks pack metadata, checks snapshot/tree/blob structure concurrently, optionally checks unused blobs, reads selected data packs, collects salvage pack IDs, prints repair guidance, and returns a fatal error if damage is found.

State/persistence: creates/removes temporary check cache directories unless `--with-cache` or `--no-cache`. It does not repair repositories; it only reports. Lock state is exclusive during checks.

Dependencies/integration: `internal/checker`, `repository`, `cache`, `data`, `restic`, and UI progress. Backup/copy/forget tests call check as a repository integrity oracle.

Risks/test signals: random subset selection is nondeterministic. Damaged pack guidance must stay aligned with repair commands. Tests cover parsing, subset selection, cache preparation, and snapshot-filtered read-data behavior.
