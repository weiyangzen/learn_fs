# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.h

## Purpose
Central public/internal header for e2fsck modules. It defines the global context, pass flags/options, major shared data structures, and cross-module prototypes.

## Key Structures
- `struct dir_info` and `struct dx_dir_info` for directory parent and indexed-directory metadata.
- `struct resource_track` for timing, memory, and I/O accounting.
- `struct extent_list` and fast-commit replay state used by extent rebuild and journal replay.
- `struct e2fsck_struct`, the main context object containing filesystem handle, names, logs, flags/options, maps, refcounts, dirinfo, encrypted file state, journal I/O, quota context, statistics, progress state, readahead, undo file, and fast-commit replay state.

## Options / Flags
Defines:
- fsck exit codes.
- e2fsck CLI/config options such as readonly, preen, yes/no, badblock checking, journal-only, discard, extent conversion/optimization, fullmap inode counts, unshare blocks, check encoding.
- internal flags for abort/cancel/restart, progress, journal inode creation, superblock specified, time insane, problems fixed, allocation permitted.

## API Surface
Declares pass entrypoints, context lifecycle, badblocks, dirinfo/dx-dirinfo, EA refcount, error handler, encrypted file policy helpers, extent rebuild APIs, journal APIs, logging, quota hooks, pass helpers, readahead, region allocation, rehashing, signal handling, superblock checks, and utility functions.

## Integration
Every substantial e2fsck C file in this group includes this header. It is the primary coupling point between passes and helper modules.

## Risks / Notes
Adding persistent per-run state requires updating both this header and context cleanup in `e2fsck.c`.
