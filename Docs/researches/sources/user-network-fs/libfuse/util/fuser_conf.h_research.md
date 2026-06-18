# sources/user-network-fs/libfuse/util/fuser_conf.h

## Purpose
Header exposing FUSE user configuration parsing and non-root policy helpers to mount utilities.

## Important APIs, Types, And Functions
- Extern globals `user_allow_other` and `mount_max`.
- Declares config, privilege, count, directory access, and fstype check functions.
- Defines `GETMNTENT` as either plain `getmntent` or an unescaping wrapper.

## Control Flow
No executable flow beyond the optional inline `GETMNTENT` wrapper, which unescapes fsname, dir, type, and opts in-place.

## State And Persistence
No state itself; exposes globals owned by `fuser_conf.c`.

## Dependencies And Integration Points
Included by privileged helpers and service mount code. Pulls in `sys/vfs.h`, `sys/stat.h`, and optionally `mntent.h`.

## Risks
Global config variables make tests order-dependent unless reset. The inline mtab wrapper mutates libc-returned storage, matching expected getmntent lifetime but important for callers.

## Test Signals
Build with and without `GETMNTENT_NEEDS_UNESCAPING`; verify all helper programs link exactly one definition of config globals.
