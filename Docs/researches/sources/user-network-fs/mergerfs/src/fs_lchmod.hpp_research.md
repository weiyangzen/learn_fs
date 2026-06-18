# sources/user-network-fs/mergerfs/src/fs_lchmod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lchmod.hpp` provides symlink-aware chmod behavior with platform fallbacks. The source was read as a complete 94-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lchmod`, `fchmodat(..., AT_SYMLINK_NOFOLLOW)`, `lchmod`, `lchmod_check_on_error`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_lstat.hpp", "to_neg_errno.hpp", <string>, <sys/stat.h>, <fcntl.h>, <sys/stat.h>. Used by chmod and metadata-copy paths. Linux symlink chmod support depends on kernel/filesystem behavior.

## Risks and Edge Cases

Used by chmod and metadata-copy paths. Linux symlink chmod support depends on kernel/filesystem behavior.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
