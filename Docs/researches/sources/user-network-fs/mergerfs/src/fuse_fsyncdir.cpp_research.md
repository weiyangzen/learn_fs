# sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp` declares directory fsync unsupported after validating the directory handle. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fsyncdir`, `fh`, `DirInfo`, `-EBADF`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fsyncdir` converts `fh` to `DirInfo`, returns `-EBADF` if invalid, otherwise `-ENOSYS`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fsyncdir.hpp", "errno.hpp", "dirinfo.hpp", "fs_fsync.hpp", "fuse.h", <string>, <vector>. Callers must tolerate unsupported directory fsync.

## Risks and Edge Cases

Callers must tolerate unsupported directory fsync.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
