# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs.h

Defines ext2/ext3/ext4-compatible on-disk superblock structures and in-memory mount-derived state. `struct ext2fs` mirrors the superblock, including classic ext2 fields and many ext4-era fields; `struct m_ext2fs` stores computed block size, shifts/masks, group descriptor count, inode table layout, max file size, and loaded group descriptors.

The header defines supported feature masks: this implementation supports sparse super and large files as RO-compatible features and filetype as an incompatible write-capable feature, while several ext4 incompat flags are tolerated only for read-only handling. It also defines group descriptors, sparse-super group selection, byte-swap/load/save macros, block/device conversion macros, inode/block group calculations, block offset/rounding helpers, free-space calculation, and `NINDIR`.
