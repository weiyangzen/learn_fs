# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/cfs.c

9P caching proxy filesystem that fronts a remote 9P server with a local block cache.

Key behavior:
- Parses options for remote address/server file, cache partition, formatting, authentication, debug, stats, and stdio mode.
- `mountinit` connects to the remote server and mounts a local pipe as the client-facing service.
- `cachesetup` opens/formats/initializes the cache partition with server identity checking.
- Main `io` loop receives client 9P messages, dispatches by type, and delegates or handles locally.
- `rversion`, `rauth`, `rattach`, `rwalk`, `ropen`, `rcreate`, `rclunk`, `rremove`, `rstat`, and `rwstat` maintain local fid/qid state while forwarding most operations.
- `rread` serves cached file bytes when present; on cache gaps, reads missing data from the server and writes it into the cache.
- `rwrite` delegates writes first, then updates cached data and inode version when safe; append-only data is not cached.
- Optional `cfsctl` stats file appears at the root when stats mode is enabled.
- `delegate` forwards a complete client request/reply pair to/from the server.
- `askserver` performs internal server reads for cache fills.
- `sendmsg`/`rcvmsg` marshal/unmarshal 9P messages and validate fids.
- `genstats` formats per-message latency/count deltas and cache byte counters.

Dependencies:
- Uses Plan 9 9P `Fcall` APIs, local inode/file/disk/block-cache modules, and `stats.h`.

Research notes:
- The cache keys by server qid path/version, invalidating stale entries on version changes.
- File lengths for cached inodes start at a maximum sentinel until server stat/read establishes real EOF.
