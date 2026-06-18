# sources/user-network-fs/mergerfs/src/fs_read.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_read.hpp` provides a small `fs::read` wrapper around the platform `read` or related syscall interface. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::read`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
