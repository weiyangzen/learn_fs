# sources/user-network-fs/nfs-utils/utils/mount/mount.c

Purpose: legacy frontend for `mount.nfs`, `mount.nfs4`, `umount.nfs`, and `umount.nfs4` when libmount is not used.

Important APIs and data: global `progname`, `nfs_mount_data_version`, `nomtab`, `verbose`, `sloppy`, and `string`. `opt_map` translates generic mount options to `MS_*` flags. `main()` dispatches to `nfsumount()` for umount names or mounts via `try_mount()`. `parse_opts()`, `parse_opt()`, `fix_opts_string()`, `init_mntent()`, `add_mtab()`, and `create_mtab()` handle option and mtab mechanics.

Control flow: CLI options are collected, non-root requests are validated against fstab and setuid status, mountpoint is canonicalized, config-file options are layered, generic flags are split from NFS-specific options, and `nfsmount_string()`, `nfs4mount()`, or `nfsmount()` performs the actual mount. Background mounts fork and retry in the child after returning success to the parent.

State and persistence: updates `/etc/mtab` through `fstab.c` unless fake/no-mtab. Adds user/users metadata for unprivileged mounts.

Dependencies and integration: uses legacy fstab/mtab code, configfile glue, NFSv2/v3, NFSv4, string mount, error handling, and utility helpers.

Risks: setuid path and user mount validation are security-sensitive. Option parsing must preserve quoted commas. Test signals include user/fstab enforcement, `-o` concatenation, `mount.nfs4` type selection, fake/no-mtab behavior, background `EX_BG`, and mtab creation/update.
