# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.h

Read status: complete, 43 lines.

Purpose: defines the VxFS fileset header on-disk structure used by `vxfs_fshead.c`.

Key content:
- `struct vxfs_fsh` contains version, fileset index, timestamp, inode counts, IAU inode, two ilist inode numbers, and link-count table inode.
- Comments state more fields follow on disk but differ by VxFS version/port and are not modeled.

Integration note: only fields needed to discover inode-list inodes are represented.
