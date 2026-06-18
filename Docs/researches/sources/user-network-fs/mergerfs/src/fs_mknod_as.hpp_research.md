# sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp` creates or opens filesystem objects as a requested uid/gid for FUSE request ownership semantics. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mknod_as`, `fs::mknod`, `lchown`, `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_mknod.hpp", "ugid.hpp", "fs_lchown.hpp". Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Risks and Edge Cases

Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
