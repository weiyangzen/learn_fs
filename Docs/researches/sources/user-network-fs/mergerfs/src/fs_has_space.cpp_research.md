# sources/user-network-fs/mergerfs/src/fs_has_space.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_has_space.cpp` answers whether a branch has enough available bytes for a pending write or move. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::has_space`, `fs::statvfs`, `StatVFS::spaceavail`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::has_space` calls `fs::statvfs`, computes available bytes through `StatVFS::spaceavail`, and compares against the requested size.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_has_space.hpp", "fs_statvfs.hpp", "statvfs_util.hpp", <string>. Feeds create/move policies and ENOSPC decisions. Free-space data can race with concurrent writers.

## Risks and Edge Cases

Feeds create/move policies and ENOSPC decisions. Free-space data can race with concurrent writers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
