# File Research: sources/os/linux/linux-stable/fs/hfs/sysdep.c

## Scope

Defines classic HFS dentry operations and timezone revalidation behavior.

## APIs And Behavior

`hfs_revalidate_dentry()` rejects RCU lookup with `-ECHILD`, accepts negative dentries, and adjusts cached inode atime/mtime/ctime if the global timezone offset changed since inode load. `hfs_dentry_operations` wires this revalidation with HFS-specific hash and compare functions.

## State And Dependencies

The file depends on `sys_tz`, per-inode `tz_secondswest`, and string helpers from `string.c`.

## Risks And Invariants

Timestamp adjustment mutates inode timestamps during dentry revalidation to preserve HFS local-time semantics. RCU path walk cannot perform this work, so RCU lookup must fall back.
