# sources/user-network-fs/mergerfs/src/fuse_access.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_access.cpp` implements FUSE `access` by checking the branch selected by access policy. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::access`, `fs::eaccess`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::access` searches policy branches for the path and calls `fs::eaccess` on the selected backing path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_access.hpp", "config.hpp", "errno.hpp", "fs_eaccess.hpp", "fs_path.hpp", <string>, <vector>. Depends on configured access/search policy and branch permissions; races with chmod/unlink are normal filesystem races.

## Risks and Edge Cases

Depends on configured access/search policy and branch permissions; races with chmod/unlink are normal filesystem races.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
