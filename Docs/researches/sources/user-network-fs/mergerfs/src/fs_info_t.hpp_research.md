# sources/user-network-fs/mergerfs/src/fs_info_t.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info_t.hpp` defines `fs::info_t`, the branch/file information record shared by policy and diagnostic code. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `struct fs::info_t`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h". It is pure data with no persistence; layout changes ripple into code consuming filesystem info snapshots.

## Risks and Edge Cases

It is pure data with no persistence; layout changes ripple into code consuming filesystem info snapshots.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
