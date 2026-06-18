# sources/user-network-fs/mergerfs/src/fs_path.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_path.hpp` centralizes mergerfs path type usage. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::path`, `std::filesystem::path`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <filesystem>. Changing this alias affects nearly every path-manipulating operation.

## Risks and Edge Cases

Changing this alias affects nearly every path-manipulating operation.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
