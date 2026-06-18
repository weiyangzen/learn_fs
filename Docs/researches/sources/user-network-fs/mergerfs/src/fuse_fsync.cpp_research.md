# sources/user-network-fs/mergerfs/src/fuse_fsync.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsync.cpp` implements fsync/fdatasync on an open file handle. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fsync`, `FileInfo`, `fs::fdatasync`, `fs::fsync`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fsync` resolves `FileInfo` and calls `fs::fdatasync` or `fs::fsync` depending on the datasync flag.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fsync.hpp", "errno.hpp", "fileinfo.hpp", "fs_fdatasync.hpp", "fs_fsync.hpp", "state.hpp", "to_neg_errno.hpp", "fuse.h". Only syncs the opened backing file; storage guarantees depend on the branch filesystem.

## Risks and Edge Cases

Only syncs the opened backing file; storage guarantees depend on the branch filesystem.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
