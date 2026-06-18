# sources/user-network-fs/sshfs/cache.c

Purpose: `cache.c` implements a FUSE operation proxy that caches attributes, directory entries, and symlink targets for sshfs.

Important APIs/types/functions: public `cache_wrap`, `cache_parse_options`, `cache_add_attr`, `cache_invalidate`, and `cache_get_write_ctr`; internal `struct cache`, `struct node`, directory entry/file-handle wrappers, cache cleanup, lookup/purge helpers, cached `getattr`, `readlink`, `opendir/readdir/releasedir`, mutating operation invalidators, and `cache_fill`.

Control flow: `cache_wrap` records the underlying operations, creates a GLib hash table, initializes the mutex, and returns a filled wrapper operation table. Reads first check cache entries under lock and fall through to underlying FUSE callbacks on miss/expiry. Directory reads either replay cached entries or open/read the underlying directory and cache a null-terminated `GPtrArray`. Mutating operations delegate first and then purge affected entries/parents on success. `cache_add_attr` accepts a write counter snapshot and only caches if no write invalidation occurred since the snapshot.

State and persistence behavior: process-local cache state in a global `cache` struct. Entries expire by stat/link/dir TTL and are cleaned by size/time thresholds. `write_ctr` increments on writes to prevent stale attrs from racing into cache.

Dependencies and integration points: depends on libfuse3 operation signatures, GLib hash/pointer arrays, pthread mutexes, and `cache.h`. `sshfs.c` wraps `sshfs_oper` with this layer when `dir_cache` is enabled.

Risks: path-prefix child invalidation uses `strncmp(key,path,strlen(path))`, so `/foo` also matches `/foobar`. Directory cache replay ignores filler errors. `cache_init` assumes underlying `init` exists. Some indentation suggests legacy style but not behavior. TTL cache may expose stale remote state between invalidations.

Test signals: tests should cover stat/readlink/readdir hits and expiry, write-counter stale attr rejection, parent purge on create/delete/rename, prefix invalidation edge cases, and cache disabled/enabled integration via sshfs options.
