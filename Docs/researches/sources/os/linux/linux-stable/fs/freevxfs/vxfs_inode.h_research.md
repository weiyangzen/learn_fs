# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_inode.h

This header defines VxFS on-disk inode structures, extent organization formats, typed extent formats, and the in-core inode-private structure.

Major responsibilities:
- Define VxFS inode size and counts for direct, indirect, immediate, and typed extent descriptors.
- Declare immediate-data, ext4-style extent, typed extent, and typed-dev4 descriptor structures.
- Declare the on-disk `struct vxfs_dinode`.
- Declare the in-core `struct vxfs_inode_info`, embedding `struct inode`.
- Provide convenience macros for union fields and the `VXFS_INO()` container helper.

Important design points:
- VxFS supports multiple inode data organizations, represented by a union in both disk and memory forms.
- Typed extent headers encode extent type in the top byte and logical offset in the lower 56 bits.
- The in-core inode stores already-converted common scalar fields, while organization-specific unions remain in disk form until interpreted.
- The inode cache is configured in `vxfs_super.c` to allow safe usercopy of the immediate-data region.

Key invariants:
- `VXFS_ISIZE` is 256 bytes and is used for inode-list block/page offset calculations.
- Immediate data is `VXFS_NIMMED` bytes.
- `VXFS_TYPED_PER_BLOCK(sb)` depends on the mounted block size.
- `VXFS_INO()` is the canonical conversion from VFS inode to VxFS inode-private data.

External interfaces:
- Used by all FreeVxFS implementation files that inspect or allocate inodes.
