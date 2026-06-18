# sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp` implements FUSE `copy_file_range` for two open mergerfs file handles. The source was read as a complete 78-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::copy_file_range`, `FileInfo`, `fs::copy_file_range`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::copy_file_range` resolves source and destination `FileInfo` objects from state and delegates to `fs::copy_file_range` with explicit offsets.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_copy_file_range.hpp", "errno.hpp", "fileinfo.hpp", "fs_copy_file_range.hpp", "state.hpp", "fuse.h", <stdio.h>. Requires both handles to be valid and opened on backing files. Cross-branch/kernel copy semantics determine performance and errors.

## Risks and Edge Cases

Requires both handles to be valid and opened on backing files. Cross-branch/kernel copy semantics determine performance and errors.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
