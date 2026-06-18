# sources/user-network-fs/mergerfs/src/fs_statx.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statx.hpp` wraps Linux `statx` when build support is available. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::statx`, `fuse_statx`, `struct statx`, `MERGERFS_SUPPORTED_STATX`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "fuse_kernel.h", <string>, <fcntl.h>, <sys/stat.h>, "supported_statx.hpp". Used by richer getattr paths. ABI compatibility between `fuse_statx` and `struct statx` is critical.

## Risks and Edge Cases

Used by richer getattr paths. ABI compatibility between `fuse_statx` and `struct statx` is critical.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
