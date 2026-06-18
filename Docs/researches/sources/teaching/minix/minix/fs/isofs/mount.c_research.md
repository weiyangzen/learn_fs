# File Research: sources/teaching/minix/minix/fs/isofs/mount.c

This file implements isofs mount, mountpoint marking, and unmount.

Entry points:
- `fs_mount(dev, flags, root_node, res_flags)`: opens the device read-only, reads volume descriptors, and returns root inode metadata.
- `fs_mountpt(ino_nr)`: validates inode exists, is not already mounted on, and is a directory, then marks mountpoint.
- `fs_unmount()`: releases primary volume descriptor/root inode, closes device, and checks inodes.

Important behavior:
- Mount ignores write flags and always opens with `BDEV_R_BIT`.
- Root UID/GID returned to VFS are `SYS_UID`/`SYS_GID`.
- `check_inodes()` currently does not actually detect active inodes.

Role:
- Bridges fsdriver mount lifecycle with ISO9660 volume descriptor parsing in `super.c`.
