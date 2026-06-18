# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_metafile.c

This file implements metadata inode flag stamping and global space reservation accounting for metadata files, especially realtime metadata btrees.

Major responsibilities:
- Map metadata file type enum values to strings with `xfs_metafile_type_str`.
- Mark an inode as a metadata file/directory via `xfs_metafile_set_iflag`.
- Clear metadata inode marking via `xfs_metafile_clear_iflag`.
- Determine whether metadata file reservations are critically low.
- Account metadata file block allocation/freeing against the reservation and superblock counters.
- Initialize and free the global metadata file reservation.

Metadata inode stamping:
- Clears ordinary permission bits.
- Sets uid/gid to root.
- Applies required metadata file or metadata directory `di_flags`.
- Clears DAX.
- Sets `XFS_DIFLAG2_METADATA`.
- Stores the metadata type in `i_metatype`.
- Moves inode stats from active to metadata.

Reservation behavior:
- Reservation is protected by `m_metafile_resv_lock`.
- Available reservation blocks are hidden via delalloc/free-block accounting.
- Allocation first consumes reservation, then falls back to free blocks or transaction reservation.
- Freeing returns blocks to reservation up to target, then to filesystem free blocks.
- Reservation initialization scans realtime groups for rtrmap and rtrefcount inode usage and target reserve sizes.
- Target reservation is capped to one quarter of data blocks.

Risk notes:
- Reservation overruns are expected only for rmap btrees and are handled specially.
- Incorrect reservation accounting can desynchronize in-core free counters and on-disk superblock counters.
- Metadata inode stats must be kept balanced when setting/clearing metadata flags.
