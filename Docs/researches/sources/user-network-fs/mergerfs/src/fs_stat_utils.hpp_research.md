# sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp` provides portable helpers for reading and writing stat timestamp fields. The source was read as a complete 79-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `st_atim/st_mtim`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <sys/stat.h>, <sys/types.h>, <unistd.h>. Important for timestamp code portability; wrong field selection breaks utimens behavior.

## Risks and Edge Cases

Important for timestamp code portability; wrong field selection breaks utimens behavior.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
