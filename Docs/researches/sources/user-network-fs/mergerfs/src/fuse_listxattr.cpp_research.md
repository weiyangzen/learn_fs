# sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp` implements FUSE listxattr across policy-selected branch instances. The source was read as a complete 168-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::listxattr`, `llistxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::listxattr` lists config keys for control files, honors global xattr mode, and concatenates each branch `llistxattr` result.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_listxattr.hpp", "config.hpp", "errno.hpp", "fs_llistxattr.hpp", "xattr.hpp", "fuse.h", <filesystem>, <string>. Duplicate names can appear from multiple branches; size can change between probe and fill.

## Risks and Edge Cases

Duplicate names can appear from multiple branches; size can change between probe and fill.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
