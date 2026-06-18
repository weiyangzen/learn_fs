# sources/user-network-fs/mergerfs/src/fs_inode.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_inode.hpp` declares virtual inode algorithms and helpers. The source was read as a complete 91-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Algo`, `set_algo`, `get_algo`, `calc`, `stat`, `fuse_statx`, `ReaddirCalc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fs_path.hpp", "fuse_kernel.h", <cstddef>, <string>, <string_view>, <sys/stat.h>. Integrated with getattr/readdir/fgetattr; tests should cover stable inode identity and collision-prone modes.

## Risks and Edge Cases

Integrated with getattr/readdir/fgetattr; tests should cover stable inode identity and collision-prone modes.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
