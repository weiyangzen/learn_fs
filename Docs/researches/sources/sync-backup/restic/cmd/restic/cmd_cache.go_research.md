# sources/sync-backup/restic/cmd/restic/cmd_cache.go

Purpose: implements `restic cache`, listing and cleaning local repository cache directories.

Important APIs/types/functions: `CacheOptions` includes `Cleanup`, `MaxAge`, and `NoSize`. `runCache` validates arguments/cache settings, chooses default cache directory, removes old cache dirs in cleanup mode, or renders a table of cache IDs, age, old status, and size. `dirSize` recursively sums file sizes.

Control flow/state: refuses arguments and disabled cache. In cleanup mode it calls `cache.OlderThan` and `os.RemoveAll` for each old cache directory. In list mode it reads `cache.All`, sorts by modification time, computes sizes unless disabled, shortens normal repo IDs to 10 chars, and prints a summary.

Dependencies/integration: `internal/backend/cache`, UI progress/table helpers, and global cache options. It mutates only local cache directories, not repositories.

Risks/test signals: `os.RemoveAll` on computed paths is destructive if cache directory discovery is wrong. `dirSize` can be slow for large caches. No dedicated tests in this subset; behavior is indirectly exercised by command integration and cache package tests elsewhere.
