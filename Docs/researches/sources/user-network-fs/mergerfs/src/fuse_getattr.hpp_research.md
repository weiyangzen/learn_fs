# sources/user-network-fs/mergerfs/src/fuse_getattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getattr.hpp` declares the FUSE `getattr` operation entry point. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `getattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h", "fs_path.hpp", <sys/types.h>, <sys/stat.h>, <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
