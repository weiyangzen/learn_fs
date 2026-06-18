# sources/user-network-fs/mergerfs/src/fs_realpathize.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_realpathize.hpp` declares vector in-place canonicalization for path strings. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `std::vector<std::string>`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <vector>. Used in path normalization after glob/config parsing.

## Risks and Edge Cases

Used in path normalization after glob/config parsing.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
