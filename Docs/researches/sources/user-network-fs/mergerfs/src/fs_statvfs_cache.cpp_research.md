# sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp` provides a process-global timeout-based statvfs cache. The source was read as a complete 148-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `statvfs_cache`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`statvfs_cache` delegates directly when timeout is zero; otherwise a shared mutex allows concurrent reads and unique locked refreshes by path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_statvfs_cache.hpp", "fs_statvfs.hpp", "statvfs_util.hpp", <mutex>, <shared_mutex>, <string>, <unordered_map>, <sys/statvfs.h>. Used by free-space and readonly checks. Staleness can affect branch selection; cache state is process-local.

## Risks and Edge Cases

Used by free-space and readonly checks. Staleness can affect branch selection; cache state is process-local.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
