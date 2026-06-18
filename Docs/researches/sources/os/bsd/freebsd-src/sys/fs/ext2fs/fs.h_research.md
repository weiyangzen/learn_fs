# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/fs.h

## Purpose
Defines ext2 filesystem placement constants and low-level block/inode geometry macros used by kernel ext2fs code.

## Main Elements
- Superblock constants: `SBLOCK`, `SBLOCKSIZE`, `SBLOCKOFFSET`, and `SBLOCKBLKSIZE`.
- Defines `MAXMNTLEN`, `EXT2_MAXCONTIG`, and Orlov allocator tuning constants `AFPDIR` and `AVGDIRSIZE`.
- Provides block conversion macros `fsbtodb()` and `dbtofsb()`.
- Provides inode placement macros `ino_to_cg()`, `ino_to_fsba()`, and `ino_to_fsbo()`.
- Provides group/block mapping macros `dtog()` and `dtogd()`.
- Provides fast block offset, logical block, byte size, fragment count, and fragment rounding macros.
- Defines `blksize()` as fragment size because FreeBSD ext2fs does not support ext2 fragments separately from blocks.
- Defines `INOPB()`, `NINDIR()`, and optional extent debug logging macro.

## Dependencies And Integration
Used by mount, inode loading, bmap, allocation, lookup, read/write, and truncation code.

## Risk Notes
These macros assume validated mount geometry and no fragment/block size divergence. Bad inputs here propagate directly into disk block addressing.
