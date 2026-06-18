# sources/user-network-fs/nfs-utils/support/include/xstat.h

## Purpose
Declares stat wrappers that can use newer statx/no-sync behavior when available.

## Important APIs, Types, and Functions
`xlstat()` and `xstat()`.

## Control Flow
Callers request lstat/stat semantics through wrappers; implementation may choose statx or traditional syscalls.

## State and Persistence Behavior
No state in the header. Filesystem metadata is read from the live filesystem.

## Dependencies and Integration Points
Used by misc and export path code.

## Risks and Edge Cases
Wrapper semantics must match lstat/stat closely, especially symlink behavior and errno.

## Test Signals
Test symlink and regular file metadata, missing paths, statx-enabled and fallback builds.
