# sources/user-network-fs/nfs-utils/utils/mount/nfsumount.c

Purpose: legacy umount helper for NFS filesystems when libmount is not used.

Important APIs and data: `nfsumount(argc, argv)` parses `-f`, `-v`, `-n`, `-r`, `-l`, and `-h`. Internal `del_mtab()` performs `umount`, `umount2(MNT_FORCE)`, or `umount2(MNT_DETACH)` and updates mtab. `try_remount()` remounts busy filesystems read-only for `-r`. `nfs_umount_is_vers4()` checks `/proc/mounts` to decide whether an advisory MOUNT `UMNT` call is needed.

Control flow: input may be a mountpoint or `host:dir`; mtab is searched backward. Non-root users may unmount only entries with `users` or matching `user=<name>`. For mounted legacy NFS and non-lazy unmounts, `nfs_umount23()` sends advisory server cleanup before local umount. Successful or already-gone unmounts remove mtab entries.

State and persistence: globals track force/lazy/remount plus shared verbose/nomtab. Persistent state is `/etc/mtab` updates and remote mountd rmtab advisory cleanup.

Dependencies and integration: uses `fstab.c`, parse_opt, parse_dev, network unmount helpers, mount constants, and error reporting.

Risks: unmount behavior must not report failure solely because advisory UMNT failed. User permission checks rely on mtab contents. Test signals include force/lazy/read-only remount, NFSv4 skip, non-root user/users permissions, missing mtab entry behavior, and mtab deletion on `EINVAL`/`ENOENT`.
