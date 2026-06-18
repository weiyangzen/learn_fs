# File Research: sources/local-fs/gfs2-utils/gfs2/init.d/gfs2

This shell script is a SysV init helper for mounting and unmounting GFS2 filesystems configured in `/etc/fstab`.

It supports `start`, `stop`, `status`, `restart`, `reload`, `force-reload`, `condrestart`, and `try-restart`. It sources distro-specific configuration from `/etc/sysconfig/*` or `/etc/default/*`, selects a lock file path, requires `/proc/mounts`, and computes:
- `GFS2FSTAB`: non-`noauto` GFS2 mountpoints from `/etc/fstab`.
- `GFS2MTAB`: active GFS2 mountpoints from `/proc/mounts`, excluding `/`.

`start` runs `mount -a -t gfs2`, touches the lock file, and reports status. `stop` runs `umount -a -t gfs2`, attempts `modprobe -r gfs2`, removes the lock file, and reports status. `status` detects stale lock files and prints configured/active mountpoints.

Risks and notes:
- It assumes legacy cluster stack dependencies (`cman`, `gfs_controld`).
- Some variable expansions are unquoted, matching older init-script style but potentially fragile for unusual paths.
- It exits `6` when no GFS2 fstab entries are configured.
