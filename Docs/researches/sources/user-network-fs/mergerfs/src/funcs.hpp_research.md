# sources/user-network-fs/mergerfs/src/funcs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/funcs.hpp` aggregates all configured FUSE operation policies. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Funcs`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "func.hpp". Stored in global config and consulted by FUSE handlers.

## Risks and Edge Cases

Stored in global config and consulted by FUSE handlers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
