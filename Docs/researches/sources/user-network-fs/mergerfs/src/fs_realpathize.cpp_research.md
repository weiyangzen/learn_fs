# sources/user-network-fs/mergerfs/src/fs_realpathize.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_realpathize.cpp` canonicalizes a vector of path strings in place. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::realpathize`, `fs::realpath`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::realpathize` calls `fs::realpath` for each entry and replaces only entries that resolve successfully.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_realpathize.hpp", "fs_realpath.hpp", <string>, <vector>. Used by branch/config normalization. Failed resolution leaves original paths intact.

## Risks and Edge Cases

Used by branch/config normalization. Failed resolution leaves original paths intact.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
