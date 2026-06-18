# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_crc.h

This header centralizes HAMMER CRC calculation, setting, and testing for blockmaps, freemap layers, volume headers, FIFO heads, B-Tree nodes, B-Tree leaf data, and mirror record heads. It supports compatibility across HAMMER volume versions that use different CRC algorithms.

CRC version behavior:
- For volume versions up to 6, CRCs use `crc32`.
- For volume version 7 and later, CRCs use `iscsi_crc32`.
- Test functions first check the current-version CRC and, for version 7 or newer, also accept a version-6 CRC. This supports upgraded filesystems whose existing metadata has not yet been rewritten with the newer algorithm.
- Newly created or rewritten metadata uses the mounted filesystem’s current version.

Covered structures:
- Blockmap entries: `hammer_crc_get/set/test_blockmap`.
- Freemap layer1 entries: `hammer_crc_get/set/test_layer1`.
- Freemap layer2 entries: `hammer_crc_get/set/test_layer2`.
- Volume headers: `hammer_crc_get/set/test_volume`, combining two CRC ranges around the stored CRC field.
- FIFO heads: `hammer_crc_get/set/test_fifo_head`, excluding the CRC field.
- B-Tree nodes: `hammer_crc_get/set/test_btree`, excluding the first CRC field.
- B-Tree leaf data: `hammer_crc_get/set/test_leaf`.
- Mirror record heads: `hammer_crc_get/set/test_mrec_head`, always using `crc32`.

Leaf-data special cases:
- Zero-length data returns CRC zero.
- Inode record data CRC excludes atime and mtime fields by using `HAMMER_INODE_CRCSIZE`, allowing those timestamp fields to be updated in place.
- Kernel invariant checks assert inode data length matches `struct hammer_inode_data` when appropriate.

Userspace/kernel split:
- When not compiling in kernel mode, the file declares CRC function prototypes because userspace cannot include the kernel `systm.h` declarations.

Architectural role:
- This header lets blockmap, B-Tree, I/O, recovery, mirroring, and userspace tooling share consistent integrity rules.
- The compatibility fallback is important for online upgrades and gradual metadata/data CRC modernization through reblocking.
