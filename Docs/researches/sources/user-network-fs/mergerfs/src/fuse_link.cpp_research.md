# sources/user-network-fs/mergerfs/src/fuse_link.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_link.cpp` implements hard-link creation across mergerfs branches with configurable EXDEV handling. The source was read as a complete 350-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::link`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::link` attempts path-preserving or create-policy hard links, clones parent dirs when needed, gets final attributes, and can convert EXDEV into symlinks per config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_link.hpp", "config.hpp", "errno.hpp", "fs_clonepath.hpp", "fs_link.hpp", "fs_lstat.hpp", "fs_path.hpp", "fuse_getattr.hpp". Hard links cannot cross filesystems; symlink fallback disables cache because the visible type differs from the requested regular link.

## Risks and Edge Cases

Hard links cannot cross filesystems; symlink fallback disables cache because the visible type differs from the requested regular link.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
