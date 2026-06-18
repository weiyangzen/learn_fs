# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_fshead.h

This header defines the VxFS fileset header structure fields used by the FreeVxFS driver.

Major responsibilities:
- Declare `struct vxfs_fsh`, the on-disk fileset header subset.
- Provide fields for fileset version/index, modification time, inode counts, allocation units, quota, maximum inode, IAU inode, inode-list inode numbers, and link-count table inode.
- Document that additional fields exist on disk but vary across VxFS versions and ports.

Important design points:
- The driver intentionally models only the stable fields needed to discover inode lists.
- `fsh_ilistino[0]` is used by `vxfs_read_fshead()` to find structural and primary inode-list inodes.
- All numeric fields are VxFS disk-endian values and must be converted through the mounted superblock's byte-order helpers.

Key invariants:
- This structure is not a complete vendor VxFS fileset header.
- Consumers must not assume fields beyond the declared subset are present or uniform across versions.

External interfaces:
- Used only by `vxfs_fshead.c`.
