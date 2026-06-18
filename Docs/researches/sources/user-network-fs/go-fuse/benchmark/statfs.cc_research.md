# sources/user-network-fs/go-fuse/benchmark/statfs.cc

Purpose: libfuse C benchmark filesystem used as a comparison point for stat-heavy workloads.

Important APIs/functions: `StatFs::readFrom` loads paths from `$STATFS_INPUT` into an `unordered_map<string,bool>` indicating directory vs file; `StatFs::GetAttr` handles root, known directories, and known files, optionally sleeping for `$STATFS_DELAY_USEC`; `global_getattr` bridges to libfuse; `main` reads env config, initializes `fuse_operations.getattr`, and calls `fuse_main`.

Control flow/state: global singleton `global`; in-memory map of path metadata; read-only getattr-only filesystem.

Dependencies/integration: compiled with libfuse headers/libs by `Makefile`; invoked by `BenchmarkLibfuseHighlevelThreadedStat`. Risks include no null check after `fopen`, fixed 1024-byte input line buffer, global state, and libfuse version/API assumptions. Test signal is benchmark startup and stat success.
