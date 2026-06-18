# sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp` approximates statvfs without following a final symlink. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lstatvfs`, `O_NOFOLLOW|O_PATH`, `fstatvfs`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "errno.hpp", "fs_close.hpp", "fs_open.hpp", "fs_fstatvfs.hpp", <cstdint>, <string>. Used when mount/filesystem data is needed for symlink paths. `O_PATH` portability is guarded by fallback defines.

## Risks and Edge Cases

Used when mount/filesystem data is needed for symlink paths. `O_PATH` portability is guarded by fallback defines.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
