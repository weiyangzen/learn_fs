# File Research: sources/os/bsd/openbsd-src/sbin/mount/mount.c

`mount.c` implements the generic OpenBSD `mount` command. It lists current mounts, mounts fstab entries with `-a`/`-A`, filters by type and network/non-network selection, handles updates, infers filesystem type from NFS-like specs or disklabels, builds helper arguments, and execs `/sbin/mount_<type>` or `/usr/sbin/mount_<type>`.

`mountfs()` canonicalizes the mount point, merges fstab and command-line options with command-line priority, forces root mounts to use `update`, optionally skips already mounted filesystems, transforms option strings into helper argv entries, forks, execs the helper, waits, and prints the resulting mount when verbose.

Printing paths convert `statfs` flags to human-readable options and include filesystem-specific display for NFS, MFS, MSDOS, CD9660, and TMPFS. `disklabelcheck()` compares fstab type to disklabel type and warns about mismatches, with compatibility exceptions.

Security/operational details: the program pledges `stdio rpath disklabel proc exec`, runs helpers rather than calling `mount(2)` directly for most filesystems, and signals `mountd` by reading `/var/run/mountd.pid` after successful root mounts.
