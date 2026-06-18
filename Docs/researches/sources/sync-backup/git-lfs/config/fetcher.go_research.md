<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/fetcher.go -->
# sources/sync-backup/git-lfs/config/fetcher.go

## Research

`fetcher.go` defines the minimal `Fetcher` interface used by configuration environments. It requires `Get`, `GetAll`, and `All`, allowing OS variables, Git config, delayed sources, and maps to be consumed uniformly.

The interface’s semantics matter: `Get` returns one string and presence, `GetAll` returns all values or an empty slice, and `All` must return a copy of key/value pairs for sources where mutation matters. There is no control flow or state in the file. Integration points are `EnvironmentOf`, `GitFetcher`, `mapFetcher`, `OsFetcher`, `URLConfig`, and tests. Risks are implementation-specific differences: `OsFetcher.All` returns nil, `MapFetcher.GetAll` can return nil, and `GitFetcher` canonicalizes keys before lookup.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/fetcher.go -->
