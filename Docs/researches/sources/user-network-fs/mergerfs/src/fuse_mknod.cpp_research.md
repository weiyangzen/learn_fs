# sources/user-network-fs/mergerfs/src/fuse_mknod.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mknod.cpp` implements FUSE mknod with branch create policy and ACL-aware mode handling. The source was read as a complete 177-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::mknod`, `mknod_as`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::mknod` mirrors mkdir flow for node creation: parent search, create-branch selection, clonepath, `mknod_as`, and retry after read-only refresh.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_mknod.hpp", "config.hpp", "errno.hpp", "error.hpp", "fs_acl.hpp", "fs_mknod_as.hpp", "fs_clonepath.hpp", "fs_path.hpp". Special file creation depends on privileges and backing filesystem support; partial success can diverge branches.

## Risks and Edge Cases

Special file creation depends on privileges and backing filesystem support; partial success can diverge branches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
