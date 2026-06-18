# sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp` implements getattr for an open file handle. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fgetattr`, `fstat`, `fs::inode::calc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fgetattr` calls `fstat`, rewrites inode through `fs::inode::calc`, and fills FUSE cache timeouts from config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fgetattr.hpp", "config.hpp", "errno.hpp", "fileinfo.hpp", "fs_fstat.hpp", "fs_inode.hpp", "state.hpp", "fuse.h". Keeps open-unlinked files stattable through the fd. Inode algorithm changes can affect observed identity.

## Risks and Edge Cases

Keeps open-unlinked files stattable through the fd. Inode algorithm changes can affect observed identity.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
