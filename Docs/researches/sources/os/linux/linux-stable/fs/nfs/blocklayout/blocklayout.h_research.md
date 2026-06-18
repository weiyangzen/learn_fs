# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.h

Defines pNFS block layout driver data structures and cross-file interfaces.

Key contents:
- Constants for page sectors, sector size, max UUIDs/devices, and UUID length cap.
- `pnfs_block_volume` describes simple, slice, concat, stripe, and SCSI volume forms.
- `pnfs_block_dev_map` maps logical offsets to block devices and disk offsets.
- `pnfs_block_dev` embeds an NFS deviceid node and describes composed block devices, children, chunking, opened bdev file, flags, SCSI reservation key, and map callback.
- `pnfs_block_extent` records file-sector to volume-sector mappings, state, device, length, and commit tag.
- `pnfs_block_layout` owns read/write extent rbtrees, extent lock, SCSI-layout flag, and last-written byte.
- Inline helpers convert layout headers/segments to `pnfs_block_layout`.
- Declares device management, extent tree, layoutcommit, and rpc_pipefs interfaces implemented by sibling files.

Research relevance:
- This header explains the structures consumed by `blocklayout.c` for BIO mapping, extent lookup, and layoutcommit tracking.
