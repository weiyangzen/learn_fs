# File Research: sources/os/linux/linux/fs/attr.c

## Summary
Implements generic VFS attribute-change validation and update helpers for chmod/chown/truncate/time changes.

## Main Responsibilities
- Decide when setuid/setgid bits should be dropped.
- Validate ownership, group, mode, timestamp, size, immutable, append-only, verity, and swapfile constraints.
- Copy simple attribute updates into inodes.
- Handle idmapped mount permission and mapping checks.
- Drive `notify_change()` security hooks, delegation breaking, filesystem `setattr`, and fsnotify.

## Key APIs
- `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`.
- `setattr_prepare()`.
- `inode_newsize_ok()`.
- `setattr_copy()`.
- `may_setattr()`.
- `notify_change()`.

## Important Behavior
`setattr_prepare()` checks truncation limits first, then owner/group/mode/time permissions unless `ATTR_FORCE` is set. It can invoke `security_inode_killpriv()` for `ATTR_KILL_PRIV`.

`inode_newsize_ok()` rejects negative sizes, enforces `RLIMIT_FSIZE` and `s_maxbytes` on extension, sends `SIGXFSZ` when appropriate, and rejects truncation of in-use swapfiles.

`setattr_copy()` updates uid/gid/mode and timestamps but intentionally does not update inode size or mark the inode dirty. Multigrain timestamp inodes use `setattr_copy_mgtime()` to keep ctime ordering coherent.

`notify_change()` rejects chmod on symlinks, truncates requested timestamps to filesystem granularity, handles privilege and setid stripping, validates idmapped uid/gid mappings, runs LSM hooks, breaks delegations unless `ATTR_DELEG` is set, calls filesystem `->setattr` or `simple_setattr`, then sends fsnotify and post-setattr security notification.

## Risks
Callers must hold the inode `i_rwsem` exclusively for `notify_change()` and `setattr_copy()`. Attribute flags have subtle interactions, especially `ATTR_MODE` with `ATTR_KILL_SUID/SGID`, idmapped mounts, invalid uid/gid mappings, multigrain timestamps, and delegation retry handling.
