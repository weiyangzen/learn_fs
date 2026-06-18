# sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp` moves a file from one branch to another and reopens it on the destination branch. The source was read as a complete 148-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `movefile_and_open`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`movefile_and_open` selects a destination branch, checks original flags and size, verifies free space, clones parent directories, copies, reopens without create/truncate/excl bits, and unlinks the source.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_movefile_and_open.hpp", "base_types.h", "errno.hpp", "fs_clonepath.hpp", "fs_close.hpp", "fs_copyfile.hpp", "fs_file_size.hpp", "fs_findonfs.hpp". Used when write operations need to rebalance or satisfy policy. Copy/open/unlink is not atomic across filesystems; several failures normalize to `-ENOSPC`.

## Risks and Edge Cases

Used when write operations need to rebalance or satisfy policy. Copy/open/unlink is not atomic across filesystems; several failures normalize to `-ENOSPC`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
