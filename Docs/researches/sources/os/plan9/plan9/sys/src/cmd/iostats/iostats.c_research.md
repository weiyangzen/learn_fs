# File Research: sources/os/plan9/plan9/sys/src/cmd/iostats/iostats.c

`iostats.c` launches a command under a proxy root filesystem and reports 9P/file I/O statistics.

Key behavior:
- Usage: `iostats [-d] [-f debugfile] cmds [args ...]`.
- Forks a child command in a namespace where `/` is mounted from a pipe to the stats filesystem.
- Forks a server process that handles 9P messages from the pipe and proxies them to the real filesystem.
- Allocates shared work queues, stats, and fid hash tables.
- Dispatches 9P request types to handlers from `statsrv.c`, using blocking slave processes for open/read/write.
- On command exit, kills slave children and prints aggregate read/write/protocol throughput, per-RPC timing/counts, and per-file activity.
- Provides fid allocation, file tree caching, root initialization, path construction, fatal cleanup, path-based exec lookup, and file report aggregation.

Important dependencies:
- Includes `statfs.h` with `Extern` defined to allocate globals.
- Depends on `statsrv.c` for protocol handlers.

Notable risks/quirks:
- Fixed-size work queue and max slave process count.
- Uses shared-memory rfork patterns and intentionally simple locking assumptions.
