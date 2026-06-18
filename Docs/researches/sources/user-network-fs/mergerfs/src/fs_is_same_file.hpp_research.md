# sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp` compares two paths by device and inode without following final symlinks. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `is_same_file`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/stat.h>, <unistd.h>. Useful for clone/rename safety checks. It races with path replacement like any pathname comparison.

## Risks and Edge Cases

Useful for clone/rename safety checks. It races with path replacement like any pathname comparison.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
