# sources/user-network-fs/mergerfs/src/fs_mounts.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mounts.cpp` collects currently mounted filesystems. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mounts`, `/proc/mounts`, `setmntent/getmntent`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::mounts` reads `/proc/mounts` with `setmntent/getmntent` on Linux and is an empty stub elsewhere.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mounts.hpp", <cstdio>, <mntent.h>. Supports mount discovery/diagnostics. Non-Linux builds receive no mount data from this file.

## Risks and Edge Cases

Supports mount discovery/diagnostics. Non-Linux builds receive no mount data from this file.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
