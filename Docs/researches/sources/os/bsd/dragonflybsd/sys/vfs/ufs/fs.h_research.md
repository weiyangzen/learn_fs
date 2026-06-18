# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/fs.h

Primary FFS on-disk layout and geometry header. It defines superblock and cylinder-group structures, filesystem constants, and macros for translating between offsets, blocks, fragments, cylinder groups, and inode locations.

Key responsibilities:
- Defines boot/superblock sizes and offsets, minimum block size, mount/volume name lengths, default free-space policy, default directory allocation tuning, and reserved snapshot inode count.
- Defines `struct csum` cylinder-group summary counters.
- Defines `struct fs`, the FFS superblock, including geometry, layout offsets, masks/shifts, summary counters, clean/readonly/flags state, mount name, volume name, in-core summary pointers, cluster and directory allocation helpers, compatibility fields, max file size, masks, state, rotational layout metadata, and magic number.
- Defines filesystem magic, clean-state checksum value, inode format versions, optimization modes, softdep/unclean flags, and rotational table formats.
- Provides macros to access rotational layout tables and cylinder-group array data for both current and old cylinder group formats.
- Defines `struct cg` current cylinder group and `struct ocg` compatibility layout.
- Provides block/offset conversion macros: filesystem block to disk block, disk block to byte offset, logical block to offset, byte offset to logical block, fragments to blocks, blocks to fragments, cylinder group location, inode-to-block mapping, block map extraction, and free-space calculation.
- Provides block-size macros for current in-core inode, disk dinode, and explicit size cases, including fragment-sized final blocks.
- Exposes `inside`, `around`, and `fragtbl` table symbols.

Dependencies:
- Relies on UFS scalar types from included upstream headers and `sys/param.h` consumers.
- Used broadly by FFS allocation, softdep, mount, vnode, and filesystem utility code.

Notable risks:
- This is on-disk ABI. Structure layout, constants, and compatibility transforms must remain stable for existing FFS filesystems.
- Many macros assume power-of-two block/fragment sizes and correct superblock masks/shifts; corrupt or unvalidated superblocks can cascade into wrong disk offsets.
- The file reserves FreeBSD snapshot/pending fields for compatibility while comments state DragonFly does not implement snapshots here.
- `fs_csp`, `fs_maxcluster`, and `fs_contigdirs` are in-core pointers embedded in the superblock copy, requiring careful preservation during reload and superblock writes.
