# sources/user-network-fs/mergerfs/src/fs_info.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info.hpp` declares overloads for collecting `fs::info_t` from a path or file descriptor. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::info`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_info_t.hpp", <string>. Used by branch policy and status reporting paths.

## Risks and Edge Cases

Used by branch policy and status reporting paths.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
