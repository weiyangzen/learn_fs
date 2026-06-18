# File Research: sources/os/linux/linux-stable/fs/attr.c

## Purpose
Implements generic VFS attribute-change policy and helper logic for chmod/chown/truncate/timestamp updates.

## Main Interfaces
- `setattr_prepare()`.
- `setattr_copy()`.
- `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`.
- `inode_newsize_ok()`.
- `may_setattr()`.
- `notify_change()`.

## Important Behavior
Permission checks are idmapped-mount aware. `chown_ok()` and `chgrp_ok()` compare current credentials and capabilities through VFS uid/gid mappings. `setattr_prepare()` validates truncate size, verity immutability, chown/chgrp/chmod permissions, timestamp-setting permissions, and `ATTR_KILL_PRIV`.

`inode_newsize_ok()` enforces negative-size rejection, `RLIMIT_FSIZE`, superblock maxbytes, SIGXFSZ delivery, and swapfile truncation denial. `setattr_copy()` updates uid/gid/mode and timestamps, with special multigrain timestamp handling through `setattr_copy_mgtime()`.

`notify_change()` is the central VFS path: it checks immutability/append restrictions, normalizes timestamps, handles killpriv and setid-bit removal, validates id mappings, calls LSM hooks, breaks delegations unless `ATTR_DELEG` is set, dispatches filesystem `->setattr` or `simple_setattr`, then emits fsnotify and post-setattr hooks.

## Cross-File Relationships
Used broadly by filesystem `->setattr` implementations and truncate/chmod/chown paths. It coordinates with LSM, fsnotify, delegation breaking, idmapped mounts, POSIX permissions, and simple filesystem helpers.

## Risks / Review Notes
`notify_change()` requires the target inode locked exclusively. Callers must handle `-EWOULDBLOCK` delegation retry correctly when using `delegated_inode`. Changes to idmapping or setid-bit rules have wide VFS security impact.
