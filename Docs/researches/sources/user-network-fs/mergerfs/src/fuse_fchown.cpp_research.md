# sources/user-network-fs/mergerfs/src/fuse_fchown.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fchown.cpp` implements fchown on an open file handle. The source was read as a complete 64-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fchown`, `FileInfo`, `fs::fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fchown` resolves `FileInfo` and calls `fs::fchown` on the backing fd.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fchown.hpp", "errno.hpp", "fileinfo.hpp", "fs_fchown.hpp", "state.hpp", "fuse.h", <unistd.h>. Only the opened branch instance changes; permission/capability failures pass through.

## Risks and Edge Cases

Only the opened branch instance changes; permission/capability failures pass through.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
