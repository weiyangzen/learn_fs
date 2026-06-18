# sources/user-network-fs/mergerfs/src/fs_info.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info.cpp` builds a compact `fs::info_t` snapshot for one path or file descriptor. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::info`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::info` combines path classification, stat/statvfs or cached statvfs data, block accounting, readonly checks, and inode metadata into the output struct.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_info.hpp", "fs_info_t.hpp", "fs_path.hpp", "fs_stat.hpp", "fs_statvfs.hpp", "fs_statvfs_cache.hpp", "statvfs_util.hpp", <cstdint>. Used by branch selection, diagnostics, and policy scoring. Risks are stale cached statvfs values and concurrent file changes.

## Risks and Edge Cases

Used by branch selection, diagnostics, and policy scoring. Risks are stale cached statvfs values and concurrent file changes.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
