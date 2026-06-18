# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/media.h

This header defines CHFS on-flash filesystem node formats, distinct from EBH eraseblock headers.

Key definitions:
- Node type enum: vnode metadata, data node, directory entry, padding.
- `CHFS_NODE_HDR_SIZE`, `CHFS_MAX_NODE_SIZE`, and `CHFS_FS_MAGIC_BITMASK`.
- `struct chfs_flash_node_hdr`: common packed node header with magic, type, length, and header CRC.
- `struct chfs_flash_vnode`: packed vnode metadata node with vnode number, version, ownership, mode, size, timestamps, and node CRC.
- `struct chfs_flash_data_node`: packed data node with vnode number, version, file offset, data length, data CRC, node CRC, and flexible data payload.
- `struct chfs_flash_dirent_node`: packed directory entry node with child/parent vnode numbers, version, mctime, name length, dtype, name CRC, node CRC, and flexible name payload.
- `struct chfs_flash_padding_node`: packed padding node.

Dependencies:
- Requires fixed-width integer types from includers.
- Uses local little-endian aliases when `_LE_TYPES` is not already defined.

Design notes:
- This file is the CHFS node-level media ABI. EBH metadata decides where logical eraseblock payload starts; these node formats describe what CHFS stores inside that payload.
