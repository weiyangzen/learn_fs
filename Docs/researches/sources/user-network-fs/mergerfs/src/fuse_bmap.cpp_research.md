# sources/user-network-fs/mergerfs/src/fuse_bmap.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_bmap.cpp` declares bmap unsupported for mergerfs. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::bmap`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::bmap` ignores request fields and returns `-ENOSYS`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_bmap.hpp", "errno.hpp". Signals to callers that physical block mapping is unavailable for pooled files.

## Risks and Edge Cases

Signals to callers that physical block mapping is unavailable for pooled files.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
