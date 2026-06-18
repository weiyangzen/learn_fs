# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_dir.h

This header defines the on-disk FreeVxFS directory block and directory entry formats.

Major responsibilities:
- Declare `struct vxfs_dirblk`, the per-directory-block header containing free-space and hash metadata.
- Define `VXFS_NAMELEN` as the maximum directory entry name length.
- Declare `struct vxfs_direct`, the VxFS directory entry format with inode, record length, name length, hash link, and name bytes.
- Define directory entry alignment and size helpers.
- Define `VXFS_DIRBLKOV()` to compute directory block header overhead using the mounted filesystem byte order.

Important design points:
- The directory hash chain data exists in the format but the Linux driver does not use it for lookup; it scans directory entries linearly.
- Directory records are padded to four-byte boundaries.
- Directory block overhead depends on the number of hash chains in the block header.

Key invariants:
- Names longer than `VXFS_NAMELEN` are rejected by lookup.
- Directory iteration must skip the block header overhead at the start of each filesystem block.
- `d_reclen == 0` marks the remainder of a directory block as unusable for scanning.

External interfaces:
- Used by `vxfs_lookup.c` for lookup and readdir.
- Included by `vxfs_super.c` for statfs name length reporting.
