# sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp` implements truncate by open file handle. The source was read as a complete 60-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::ftruncate`, `FileInfo`, `fs::ftruncate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::ftruncate` resolves `FileInfo` and delegates to `fs::ftruncate` with the requested size.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_ftruncate.hpp", "errno.hpp", "fileinfo.hpp", "fs_ftruncate.hpp", "state.hpp", "fuse.h". Only changes the opened branch instance; ENOSPC/EINVAL behavior comes from the backing fs.

## Risks and Edge Cases

Only changes the opened branch instance; ENOSPC/EINVAL behavior comes from the backing fs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
