# File Research: sources/virtualization/libguestfs/daemon/mount.c

Mount-state inspection and unmount/remount helpers.

Important behavior:
- `is_root_mounted` scans `/proc/mounts` for mounts at or below `sysroot`.
- `is_device_mounted` compares `st_rdev` of the device and mounted fs names under sysroot.
- `do_umount` accepts a path or device, supports optional force/lazy flags, and uses external `umount`.
- `do_mounts` and `do_mountpoints` return mounted devices and optional mountpoints; `/dev/mapper` and `/dev/dm-*` paths are canonicalized through LVM.
- `do_umount_all` finalizes Augeas, hivex, and journal handles, sorts mount paths longest-first, then unmounts.
- `do_mount_loop` mounts a sysroot file with `-o loop`.
- `do_remount` requires explicit `rw` optional arg and remounts ro/rw.
- `do_mkmountpoint` and `do_rmmountpoint` intentionally bypass `NEED_ROOT`.

Filesystem relevance: manages the daemon’s mounted guest filesystem tree and cleanup order.
