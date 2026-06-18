# sources/user-network-fs/mergerfs/src/fs_xattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_xattr.cpp` implements higher-level extended-attribute list/get/set/copy helpers. The source was read as a complete 361-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::xattr::*`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::xattr::*` uses size-probe retry loops, converts NUL-separated attr lists to vector/string/map forms, sets maps one attr at a time, and copies attrs between fds or paths.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_xattr.hpp", "errno.hpp", "fs_close.hpp", "fs_fgetxattr.hpp", "fs_flistxattr.hpp", "fs_fsetxattr.hpp", "fs_lgetxattr.hpp", "fs_llistxattr.hpp". Shared by FUSE xattr operations and metadata-copy flows. Xattr changes between probe and read can force retries or partial copies.

## Risks and Edge Cases

Shared by FUSE xattr operations and metadata-copy flows. Xattr changes between probe and read can force retries or partial copies.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
