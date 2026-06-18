# sources/user-network-fs/nfs-utils/support/misc/mountpoint.c

## Purpose
Implements mountpoint detection by comparing a path with its parent.

## Important APIs, Types, and Functions
`check_is_mountpoint(path, mystat)` and macro wrapper `is_mountpoint()` from `misc.h`.

## Control Flow
It builds `path/..`, stats both with `mystat` or `lstat`, and returns true when device differs or inode is equal, matching common mountpoint/root detection.

## State and Persistence Behavior
No persistent state. It allocates a temporary string and reads filesystem metadata.

## Dependencies and Integration Points
Uses `xmalloc` and `misc.h`; consumed by export/cache path checks.

## Risks and Edge Cases
Trailing slashes and unusual paths depend on stat behavior. If either stat fails, result is false. Caller can choose stat vs lstat semantics.

## Test Signals
Test root directory, ordinary directory, actual mountpoint, symlink with stat/lstat handlers, missing path, and allocation cleanup.
