# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_disk.h

## Purpose
Defines HAMMER2's on-disk media ABI: allocation geometry, freemap layout, block references, inode records, PFS identity fields, volume headers, checksum/compression encodings, and the union used to interpret 64KB media buffers.

## Major Definitions
- Allocation geometry: minimum allocation is 1KB (`HAMMER2_ALLOC_MIN`, radix 10), current maximum is 64KB (`HAMMER2_ALLOC_MAX`, radix 16), logical buffer size is 16KB, physical buffer size is 64KB, and allocation/freemap segment size is 4MB.
- Indirect topology: blockrefs are 128 bytes, arranged in fully associative sets of 4 in embedded inode blocksets, with indirect blocks supporting 4KB to 64KB payloads.
- Offset encoding: `hammer2_off_t` stores a 64-byte-aligned physical offset in the high bits and the allocation-size radix in the low 6 bits; radix 0 is a special no-data value.
- Freemap geometry: reserved 4MB area per 1GB region, eight rotating freemap copies, levels from 1GB leaves through 4EB nodes, and a level-6 blockset in the volume header for 16EB reach.
- Freemap bitmap model: 4MB `hammer2_bmap_data` entries use 8 x 64-bit words, two bits per 16KB region, with `00` free, `10` possibly free, and `11` allocated.
- DMSG/cluster configuration: `hammer2_volconf` and `dmsg_lnk_hammer2_volconf` describe copy targets, PFS cluster IDs, priorities, labels, and remote paths.
- Core media objects: `hammer2_blockref`, `hammer2_blockset`, `hammer2_bmap_data`, `hammer2_inode_meta`, `hammer2_inode_data`, `hammer2_volume_data`, and `hammer2_media_data`.

## On-Disk Structures
- `hammer2_blockref` is the core recursive pointer. It carries object type, check/compression methods, copy ID, key range, mirror/modify/update tids, physical data offset, embedded directory entry or aggregate stats, and a 64-byte check area.
- `hammer2_inode_data` is exactly 1024 bytes: 256 bytes of metadata, 256 bytes of filename storage, and 512 bytes of direct data or an embedded blockset.
- `hammer2_volume_data` is exactly 64KB. It contains magic/version fields, boot/aux ranges, volume sizing, allocator counters, mirror/freemap tids, copy-existence bitmap, CRC sectors, super-root blockset, freemap blockset, volume logical offsets, and 256 copyinfo records.
- `hammer2_media_data` overlays the same 64KB physical buffer as volume data, inode data, blockset, indirect blockref array, freemap bitmap array, or raw bytes.

## Filesystem Semantics Captured Here
- HAMMER2 is COW; any modification propagates check code and mirror tid upward through the blockref tree.
- Directory entries and inodes share the blockref topology. Small file data can live directly inside the inode, making tiny files directory-local.
- PFS roots are directories under the super-root and are identified by both cluster ID (`pfs_clid`) and filesystem ID (`pfs_fsid`).
- PFS type encodings support cache, slave, soft-slave, soft-master, master, super-root, dummy, and transition states.
- Volume headers exist in four 2GB-spaced copies; the mount code can choose a consistent synchronization point after a crash.

## Important Invariants
- Many structures are packed and size-sensitive; comments repeatedly note exact 128-byte, 1024-byte, and 64KB requirements.
- The freemap assumes `HAMMER2_SET_COUNT == 4`, enforced by preprocessor checks.
- `HAMMER2_VOLUME_ALIGN` and `HAMMER2_ZONE_SEG` must align to the 4MB freemap level-0 size.
- Host byte order is the normal media format; reversed-endian compatibility would require explicit access adjustment.
- Volume versions before multi-volume support imply a single root volume; version 2 supports up to 64 volumes.

## Interactions
- Used by nearly every HAMMER2 implementation file for media layout and constants.
- `hammer2_freemap.c` consumes the freemap geometry and bitmap definitions.
- `hammer2_flush.c` updates blockref checks, mirror tids, and volume-header CRCs.
- `hammer2_inode.c` mirrors `hammer2_inode_meta` into in-memory inodes.
- `hammer2_ioctl.c` exposes PFS, inode, volume, and remote-copy fields to userland.
