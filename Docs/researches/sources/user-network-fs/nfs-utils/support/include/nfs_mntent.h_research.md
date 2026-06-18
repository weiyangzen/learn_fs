# sources/user-network-fs/nfs-utils/support/include/nfs_mntent.h

## Purpose
Declares a mount-table parser/writer wrapper derived from util-linux mount entry handling.

## Important APIs, Types, and Functions
Defines `mntFILE` with FILE pointer, pathname, line number, and error counters, plus `nfs_setmntent()`, `nfs_endmntent()`, `nfs_addmntent()`, `my_getmntent()`, and `nfs_getmntent()`.

## Control Flow
Callers open a mount table through `nfs_setmntent()`, iterate or add entries, track parse errors, and close with `nfs_endmntent()`.

## State and Persistence Behavior
Parser state is stored in `mntFILE`. Persistent state is the mounted/fstab file being read or written.

## Dependencies and Integration Points
Depends on `<mntent.h>` and support implementation files. Used by mount utilities.

## Risks and Edge Cases
Error thresholds and soft-error handling are implementation-defined. Callers must not mix raw FILE operations with wrapper state.

## Test Signals
Test malformed mount entries, write/add paths, line/error counters, and close cleanup.
