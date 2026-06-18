# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/cfs.c

This file is the main `cfs` caching 9P proxy filesystem.

Key behavior:
- Parses options for server address/file, cache partition, formatting, auth, debug, standard-io mode, server opening mode, and stats.
- Opens/mounts a remote 9P server and mounts a local proxy namespace.
- Initializes or formats the local cache partition through `cachesetup()`.
- Main `io()` loop receives 9P messages from the client and dispatches handlers.
- Delegates metadata and unsupported operations to the server while caching regular-file reads/writes.
- `rread()` serves cached file ranges from `Icache`/`file.c`; on gaps it asks the server, returns data, and writes fetched data into cache.
- `rwrite()` delegates writes first, then updates cached regular-file data unless append-only.
- Tracks qid/version changes and invalidates stale cache entries.
- Provides synthetic root `cfsctl` stats file when stats mode is enabled.
- Marshals/unmarshals 9P messages with `convS2M()`, `read9pmsg()`, and `convM2S()`.

Important details:
- Local cache identity can be tied to the remote server address; mismatches force formatting.
- `Tversion` negotiates `messagesize` with the client and passes it downstream.
- Directories and auth fids are not cached.
- The cache stores incomplete sparse ranges; gaps trigger targeted server reads.
- Statistics track per-message counts/timing and bytes from server, cache, dirs, and inserted into cache.

Filesystem relevance:
- Direct. This is a Plan 9 client-side caching filesystem proxy.
