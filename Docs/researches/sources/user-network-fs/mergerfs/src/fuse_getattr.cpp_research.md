# sources/user-network-fs/mergerfs/src/fuse_getattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getattr.cpp` implements path-based FUSE getattr and synthetic attrs for root/control files. The source was read as a complete 239-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::getattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::getattr` selects a branch, applies symlink-follow behavior, optional symlinkify conversion, virtual inode calculation, and cache timeout selection.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_getattr.hpp", "config.hpp", "errno.hpp", "fs_fstat.hpp", "fs_inode.hpp", "fs_lstat.hpp", "fs_path.hpp", "fs_stat.hpp". Core lookup path; risks are stale cache timeouts, symlink policy surprises, and inode collision/identity tradeoffs.

## Risks and Edge Cases

Core lookup path; risks are stale cache timeouts, symlink policy surprises, and inode collision/identity tradeoffs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
