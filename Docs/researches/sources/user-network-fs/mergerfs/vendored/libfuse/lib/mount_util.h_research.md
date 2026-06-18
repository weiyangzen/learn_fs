# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_util.h

## Purpose
`mount_util.h` provides shared mount-table and path utilities for the generic mount path and `fusermount`.

## Important APIs, Types, and Functions
Public helpers are `fuse_mnt_add_mount`, `fuse_mnt_umount`, `fuse_mnt_remove_mount`, `fuse_mnt_resolve_path`, and `fuse_mnt_check_fuseblk`. Internals include `mtab_needs_update`, `add_mount`, `exec_umount`, and `remove_mount`.

## Control Flow
`mtab_needs_update` skips updates when `/etc/mtab` is missing, symlinked, inside the mount, or read-only. Add/remove/update helpers fork `/bin/mount` or `/bin/umount` with fake/no-canonicalize flags while SIGCHLD is blocked. `fuse_mnt_umount` either calls `umount2` directly or delegates to `/bin/umount`. `fuse_mnt_resolve_path` canonicalizes the parent path while preserving a final component that may not yet exist. `fuse_mnt_check_fuseblk` scans `/proc/filesystems`.

## State and Persistence
The durable state touched here is the OS mount table or mtab representation. It also changes effective uid temporarily for mtab write checks.

## Dependencies and Integration Points
`mount_generic.h` uses these helpers after direct root mounts and unmounts. `fusermount.cpp` uses them for resolving mountpoints, mtab updates, and fuseblk support checks.

## Risks
Forked mount/umount commands must be present at `/bin/mount` and `/bin/umount`. The `mtab_needs_update` prefix check is path-sensitive. Temporary `setreuid` use must restore uid. Path resolution edge cases around trailing slashes, `.`, and `..` can affect mount safety.

## Test Signals
Test symlinked `/etc/mtab`, read-only mtab, missing mtab, root and non-root update paths, relative/trailing slash mountpoints, missing final component, fuseblk present/absent, and failure of fork/exec/wait.
