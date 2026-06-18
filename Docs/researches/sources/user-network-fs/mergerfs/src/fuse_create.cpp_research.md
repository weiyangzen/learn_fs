# sources/user-network-fs/mergerfs/src/fuse_create.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_create.cpp` implements FUSE create/open for new files with cache and passthrough support. The source was read as a complete 355-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::create`, `FileInfo`, `state.open_files`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::create` chooses cache flags, adjusts writeback flags, clones parent paths, creates as request uid/gid, stores `FileInfo` in `state.open_files`, and may attach a passthrough backing id.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_create.hpp", "state.hpp", "config.hpp", "fs_readlink.hpp", "errno.hpp", "fileinfo.hpp", "fs_acl.hpp", "fs_close.hpp". Central integration with config policies, branches, ACL umask handling, procfs process names, and passthrough. Impossible nodeid collisions are treated as critical errors.

## Risks and Edge Cases

Central integration with config policies, branches, ACL umask handling, procfs process names, and passthrough. Impossible nodeid collisions are treated as critical errors.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
