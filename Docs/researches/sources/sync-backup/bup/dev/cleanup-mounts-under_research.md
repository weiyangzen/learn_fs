# sources/sync-backup/bup/dev/cleanup-mounts-under

## Purpose
Polyglot shell/Python cleanup utility used by `make clean` to unmount FUSE or other mounts under target directories without relying on configured bup executables.

## Important APIs, Types, and Functions
Bootstraps a suitable Python interpreter, defines `mntent_unescape`, reads `/proc/mounts`, and runs `fusermount -uz` for FUSE filesystems or `umount -l` for others.

## Control Flow
For each target, verifies it is a directory, resolves its real path, scans mount entries, unescapes mountpoint names, and unmounts entries equal to or below the target.

## State and Persistence Behavior
Mutates system mount state; no files are written. Returns nonzero if targets are invalid or unmounts fail.

## Dependencies and Integration Points
Integrated into `GNUmakefile clean` before deleting test mount trees. Linux-specific `/proc/mounts`; no-op on platforms without it.

## Risks and Test Signals
Risks include common-prefix path checks, unmounting active mounts, missing `fusermount`, and no `/proc/mounts` on non-Linux. Signals are exit status and stderr diagnostics.
