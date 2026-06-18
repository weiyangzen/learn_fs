# sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp` implements FUSE mkdir with branch create policy and ACL-aware umask handling. The source was read as a complete 167-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::mkdir`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::mkdir` finds an existing parent branch, selects create branches, clones parent paths, applies umask only without default ACLs, creates as request uid/gid, and retries after read-only refresh.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_mkdir.hpp", "config.hpp", "errno.hpp", "error.hpp", "fs_acl.hpp", "fs_clonepath.hpp", "fs_mkdir_as.hpp", "fs_path.hpp". Partial branch creation can leave namespace divergence; readonly detection is refreshed after `-EROFS`.

## Risks and Edge Cases

Partial branch creation can leave namespace divergence; readonly detection is refreshed after `-EROFS`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
