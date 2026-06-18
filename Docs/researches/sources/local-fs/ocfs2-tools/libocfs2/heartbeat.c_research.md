# File Research: sources/local-fs/ocfs2-tools/libocfs2/heartbeat.c

Purpose: heartbeat block byte swapping and heartbeat region descriptor construction.

Key responsibilities:
- Swaps `o2hb_disk_heartbeat_block` fields on big-endian hosts.
- Builds an `o2cb_region_desc` from the heartbeat system inode and device sector size.

Important APIs:
- `ocfs2_swap_disk_heartbeat_block()`
- `ocfs2_fill_heartbeat_desc()`

Core behavior:
- Determines hardware sector size; falls back to `OCFS2_MIN_BLOCKSIZE` only when sector size cannot be determined.
- Looks up the heartbeat system inode in the system directory.
- Requires heartbeat file to be a single-level, single-record extent list.
- Verifies filesystem block size is not smaller than hardware sector size.
- Computes heartbeat region start in hardware-sector units from the physical extent block.
- Limits heartbeat region blocks to `O2NM_MAX_NODES`.

Dependencies:
- Uses `ocfs2_get_device_sectsize()`, system inode lookup, inode read, extent record helpers, and superblock block/cluster size bits.

Notable behavior:
- Returns `OCFS2_ET_BAD_HEARTBEAT_FILE` for unexpected heartbeat extent shape or insufficient heartbeat blocks.
- The descriptor borrows `fs->uuid_str` and `fs->fs_devname`; it does not allocate copies.
