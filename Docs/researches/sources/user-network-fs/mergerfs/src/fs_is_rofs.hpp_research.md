# sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp` detects read-only branch/filesystem states. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `is_mounted_rofs`, `is_rofs`, `is_rofs_but_not_mounted_ro`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_close.hpp", "fs_mktemp.hpp", "fs_path.hpp", "fs_statvfs.hpp", "fs_unlink.hpp", "statvfs_util.hpp", <fcntl.h>. Used to mark branches readonly after EROFS. Temp-file probing can leave cleanup work if close/unlink fails.

## Risks and Edge Cases

Used to mark branches readonly after EROFS. Temp-file probing can leave cleanup work if close/unlink fails.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
