# sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp` implements fallocate on an open file handle. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fallocate`, `FileInfo`, `fs::fallocate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fallocate` looks up `FileInfo` from state and delegates to `fs::fallocate`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fallocate.hpp", "state.hpp", "errno.hpp", "fileinfo.hpp", "fs_fallocate.hpp", "fuse.h". No branch policy is consulted after open; errors reflect the backing filesystem.

## Risks and Edge Cases

No branch policy is consulted after open; errors reflect the backing filesystem.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
