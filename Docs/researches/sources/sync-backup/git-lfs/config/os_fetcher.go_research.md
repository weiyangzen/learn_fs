<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/os_fetcher.go -->
# sources/sync-backup/git-lfs/config/os_fetcher.go

## Research

`os_fetcher.go` implements `OsFetcher`, a mutex-protected cached wrapper around `os.LookupEnv`. `Get` caches both present values and misses using `map[string]*string`; `GetAll` returns either a one-element slice or an empty slice; `All` returns nil because the OS environment is not enumerated here.

State persists for the lifetime of the fetcher, so environment changes after first lookup are intentionally not observed. Integration points include `Configuration.Os`, credential askpass and prompt behavior, filesystem alternates, and all environment-based flags. Risks include stale values in long-running processes, nil `All` surprising generic callers, pointer-to-local-string escape semantics being safe but subtle, and no cache invalidation for tests that modify environment variables.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/os_fetcher.go -->
