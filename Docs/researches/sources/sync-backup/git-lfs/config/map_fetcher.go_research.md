<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/map_fetcher.go -->
# sources/sync-backup/git-lfs/config/map_fetcher.go

## Research

`map_fetcher.go` provides test/in-memory `Fetcher` implementations. `MapFetcher` wraps `map[string][]string`; `UniqMapFetcher` adapts `map[string]string` into a single-value map. `Get` returns the last entry for a key, `GetAll` returns the stored slice, and `All` deep-copies the slice values into a new map.

There is no synchronization, so this fetcher is intended for immutable test/config data. It integrates with `NewFrom`, environment tests, URL config tests, and any caller needing synthetic configuration. Risks are nil maps returning nil slices, callers mutating `GetAll` slices because they are not copied, and case-sensitive lookups unlike `GitFetcher`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/map_fetcher.go -->
