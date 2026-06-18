# File Research: sources/os/linux/linux/fs/xfs/xfs_discard.h

Declares the XFS discard interface:
- `xfs_discard_extents` issues discard I/O for a prepared busy extent list.
- `xfs_ioc_trim` implements the FITRIM ioctl path.

The header forward-declares the userspace trim range, mount, and busy extent structures to keep dependencies light.
