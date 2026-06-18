# sources/user-network-fs/mergerfs/src/fs_open_fd.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_open_fd.cpp` reopens an existing file descriptor as a new descriptor with requested flags. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::open_fd`, `/proc/self/fd/<fd>`, `O_EMPTY_PATH`, `O_NOFOLLOW`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::open_fd` opens `/proc/self/fd/<fd>` on Linux or uses `O_EMPTY_PATH` on FreeBSD, clearing `O_NOFOLLOW`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_open_fd.hpp", "fmt/core.h", "fs_openat.hpp", "fatal.hpp", "procfs.hpp", "fs_openat.hpp". Used for pathless fd reopening with modified flags. Linux depends on procfs initialization.

## Risks and Edge Cases

Used for pathless fd reopening with modified flags. Linux depends on procfs initialization.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
