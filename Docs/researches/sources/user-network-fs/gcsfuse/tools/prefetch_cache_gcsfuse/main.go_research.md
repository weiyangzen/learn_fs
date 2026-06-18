# sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/main.go

Purpose: CLI wrapper for prefetching GCS objects into gcsfuse's persistent cache directory.

Important APIs/types/functions: `run(args []string)` and `main`.

Control flow: validates `cache_dir bucket_name [prefix]`, logs resolved settings, calls `prefetchCache`, and wraps failures with CLI context.

State/persistence behavior: delegates cache file creation to `prefetch.go`; this file itself only logs and exits with status 1 on error.

Dependencies/integration: paired with `prefetch.go` and standard `flag` parsing.

Risks/test signals: usage message uses `os.Args[0]` even when `run` is unit-tested with synthetic args. No explicit validation checks that cache dir exists or is writable before delegation.
