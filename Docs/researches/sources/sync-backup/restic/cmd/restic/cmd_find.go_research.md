# sources/sync-backup/restic/cmd/restic/cmd_find.go

Purpose: implements `restic find`, searching snapshots by path patterns, blob IDs, tree IDs, or pack IDs, with optional JSON output and time/snapshot filters.

Important APIs/types/functions: `FindOptions` captures pattern, ID-mode, pack display, sorting, listing, and snapshot filters. `findPattern` stores time range and normalized patterns. `statefulOutput` formats grouped normal/JSON output. `Finder` implements `findInSnapshot`, `findIDs`, `findTree`, `packsToBlobs`, `indexPacksToBlobs`, `findObjectPack`, and `findObjectsPacks`. `runFind` validates options and orchestrates the search.

Control flow: parses time bounds, rejects mixed ID modes, opens read lock, memoizes snapshots, loads index, initializes finder maps for blob/tree/pack modes, resolves pack IDs to blob/tree IDs from repository or index, filters and sorts snapshots, then either walks paths with pattern pruning or walks IDs. JSON output is emitted as arrays grouped by snapshot or object matches.

State/persistence: read-only repository access. It uses the loaded index and snapshot tree walks; no repository mutation.

Dependencies/integration: `internal/walker`, `filter.Match/ChildMatch`, snapshot filtering, repository pack/blob indexes, UI formatting, and JSON encoding.

Risks/test signals: JSON output is manually stateful and must close arrays correctly. Pack lookup falls back to index for missing pack files. Time parsing accepts multiple local formats. Integration tests cover path find, JSON output, sorting/reverse, invalid time range, pack/tree/data lookup, and pack ID resolution.
