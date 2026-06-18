# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bmap.c

This file maps UFS logical file blocks to physical disk blocks.

Key responsibilities:
- Implements `ufs_bmap`, returning the underlying device vnode and physical block number.
- Implements `ufs_bmaparray`, traversing direct, external-attribute, single-, double-, and triple-indirect block pointers.
- Implements run-length detection for sequential physical blocks.
- Handles holes by returning `-1`.
- Handles snapshots specially, returning zero-fill behavior for snapshot marker block ranges.
- Implements `ufs_getlbns`, computing the chain of logical metadata block numbers and offsets needed to reach a data block.

Important behavior:
- Uses `ufs_rw32`/`ufs_rw64` and mount byte-swap state for UFS1/UFS2 pointer reads.
- Reads indirect blocks as buffers attached to the file vnode using negative logical block numbers.
- Supports UFS2 external attribute blocks through negative block numbers in the `-1 .. -UFS_NXADDR` range.
