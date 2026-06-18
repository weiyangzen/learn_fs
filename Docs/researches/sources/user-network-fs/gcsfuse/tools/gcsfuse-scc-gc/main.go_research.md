<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go -->
# sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go

Purpose: Standalone shared chunk cache garbage collector for gcsfuse, expiring least-recently-used `.bin` cache chunks, deleting previous `.bak` expirations, removing stale `.tmp` files, and cleaning empty directories.

Important APIs, types, and functions: CLI flags are `--cache-dir`, `--target-size-mb`, `--concurrency`, `--dry-run`, and `--debug`. `FileInfo` records path, atime, mtime, and size. `Manifest` stores `.bin`, `.bak`, `.tmp`, directories, total size, and scan duration. Core functions are `scanCache`, `removeBakFiles`, `removeOldTmpFiles`, `findLRUFiles`, `expireFiles`, `cleanupEmptyDirs`, and `printFileInfo`.

Control flow: `main` configures slog, requires `cache-dir`, scans the cache, deletes previous `.bak` files, compares total `.bin` size against target, selects oldest chunks by max(atime, mtime), renames selected `.bin` files to `.bin.bak`, removes `.tmp` files older than one hour, cleans empty directories, and logs completion. Dry run logs intended work without mutation.

State and persistence behavior: Mutates filesystem cache under `cache-dir` or `cache-dir/gcsfuse-shared-chunk-cache` if present. Expiration is a rename to `.bak` so existing file handles continue working until next run deletes the `.bak`. Parallel workers delete/rename files, using atomics for counters.

Dependencies and integration points: Linux/Unix filesystem stat access via `syscall.Stat_t` for atime/mtime, shared chunk cache file naming (`.bin`, `.tmp`, `.bak`), and external scheduling by users or services. It does not interact with GCS directly.

Risks and test signals: `cleanupEmptyDirs` uses `filepath.SplitList` to estimate depth, which is path-list separator based and likely not actual directory depth; cleanup order may be wrong. Atime availability depends on mount options such as noatime/relatime; mtime fallback mitigates new files. Concurrency flag values of zero or negative could deadlock or skip workers. Unit tests cover LRU selection, .bak deletion, tmp age threshold, extension filtering, and atime/mtime ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main.go -->
