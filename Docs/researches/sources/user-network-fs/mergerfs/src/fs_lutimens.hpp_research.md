# sources/user-network-fs/mergerfs/src/fs_lutimens.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lutimens.hpp` updates symlink timestamps using the project utimensat abstraction. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lutimens`, `fs::utimensat(..., AT_SYMLINK_NOFOLLOW)`, `struct stat`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_utimensat.hpp", "fs_stat_utils.hpp". Used by metadata preservation and utimens FUSE paths. Platform timestamp support varies.

## Risks and Edge Cases

Used by metadata preservation and utimens FUSE paths. Platform timestamp support varies.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
