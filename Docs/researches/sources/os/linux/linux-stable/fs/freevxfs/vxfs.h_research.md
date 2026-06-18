# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs.h

This header defines FreeVxFS superblock structures, byte-order helpers, VxFS mode/type constants, inode organization constants, and the superblock private-data accessor.

Major responsibilities:
- Define the VxFS superblock magic, root inode number, and free extent array size.
- Represent filesystem byte order with `VXFS_BO_LE` and `VXFS_BO_BE`.
- Define bitwise disk integer types `__fs16`, `__fs32`, and `__fs64`.
- Declare the on-disk `struct vxfs_sb` fields used by the driver.
- Declare `struct vxfs_sb_info`, the in-core VxFS superblock private state.
- Provide endian conversion helpers that depend on the mounted filesystem's byte order.
- Define VxFS file mode/type bits, including regular Unix file types and VxFS internal structural inode types.
- Define inode organization types: none, ext4-style extents, immediate data, and typed extents.
- Provide macros to test VxFS inode type and organization.

Important design points:
- The on-disk superblock definition intentionally stops after the fields this driver needs.
- `vxfs_sb_info` stores raw superblock buffer state plus discovered structural inodes, OLT location, fileset header inode, initial inode-list extent, and byte order.
- The driver supports both UnixWare-style little-endian and HP-UX-style big-endian layouts through per-superblock conversion helpers.
- Internal VxFS inode types are separated from regular VFS file types and should not be exposed as normal mode bits.

Key invariants:
- `VXFS_SUPER_MAGIC` must match after applying the detected byte order.
- `VXFS_ROOT_INO` is inode 2.
- Type checks mask with `VXFS_TYPE_MASK`.
- Organization checks use `vii_orgtype`, and unsupported organization types are rejected by mapping code.

External interfaces:
- Provides shared definitions consumed by all FreeVxFS implementation files.
