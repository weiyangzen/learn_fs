# sources/user-network-fs/mergerfs/vendored/libfuse/util/fusermount.cpp

## Purpose
`fusermount.cpp` is the setuid-style helper for mounting and unmounting FUSE filesystems safely for unprivileged users.

## Important APIs, Types, and Functions
The file is a standalone `main`. Major helpers include privilege switching (`drop_privs`, `restore_privs`), mtab locking/update, unmount authorization (`may_unmount`), symlink-safe mountpoint verification (`check_is_mount*`, `chdir_to_parent`, `umount_nofollow_support`), config parsing (`read_conf`), option filtering (`do_mount`, `find_mount_flag`, `get_mnt_opts`), mountpoint permission checking (`check_perm`), fuse device open, `mount_fuse`, and `send_fd`.

## Control Flow
`main` parses `-o`, `-u`, `-z`, `-q`, help/version, resolves the mountpoint under dropped privileges, and either unmounts or mounts. Mounting opens `/dev/fuse`, reads `/etc/fuse.conf`, enforces `mount_max`, verifies mountpoint permissions, builds safe mount options, calls `mount(2)`, optionally updates mtab, sends the fuse fd to the caller over `_FUSE_COMMFD`, and handles `auto_unmount` by daemonizing and unmounting when the control socket closes. Unmounting validates ownership/mtab for root-effective helper mode and avoids symlink-following attacks.

## State and Persistence
It mutates mount table state, may update mtab, reads `/etc/fuse.conf`, and passes fds over Unix sockets. Globals include `user_allow_other`, `mount_max`, and `auto_unmount`.

## Dependencies and Integration Points
It uses `mount_util.h`, libc/POSIX mount/socket/namespace APIs, `/dev/fuse`, `/etc/fuse.conf`, and `_FUSE_COMMFD`. `mount_generic.h` execs this helper for fallback/unprivileged mounts.

## Risks
This is security-critical. `allow_other`, `dev`, `suid`, `blkdev`, mountpoint ownership, symlink races, and mtab authorization all need strict behavior. The helper assumes Linux-specific namespace and fsuid APIs. Fixed buffers and manual option parsing require bounds vigilance.

## Test Signals
Test non-root mount with/without `user_allow_other`, `mount_max`, directory and regular-file mountpoints, symlink race prevention, lazy and normal unmount, mtab symlink mode, fd passing, `auto_unmount`, missing `/dev/fuse`, and old `/proc/fs/fuse/dev` fallback.
