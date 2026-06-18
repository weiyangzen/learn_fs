# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/mke2fs.c

Purpose: Back-end ext2 filesystem constructor for `newfs_ext2fs`. It builds ext2 superblocks, group descriptors, bitmaps, inode tables, root directory, optional `lost+found`, and optional REV1 resize inode structures.

Format setup:
- Validates block/fragment sizes, sector size, power-of-two constraints, and ext2’s lack of separate fragment support.
- Defaults to conservative ext2 REV0 unless `Oflag` requests REV1.
- REV1 enables `EXT2F_COMPAT_RESIZE`, `EXT2F_INCOMPAT_FTYPE`, and sparse-super/large-file read-only-compatible features.
- Uses Linux as `e2fs_creator` for firmware/tool compatibility.

Block group layout:
- Computes `first_dblock` to preserve bootloader space.
- Chooses blocks per group as one block bitmap worth of blocks.
- Computes group descriptor blocks, inodes per group, inode table blocks, and checks whether the last group can hold required metadata plus data.
- Adjusts inode count to group and inode-table alignment.
- Builds in-memory group descriptor table, with bitmap/table locations and free block/inode counts.

Reserved resize support:
- For REV1 with resize feature, reserves group descriptor blocks for future growth up to a 1024x target, bounded by uint32 block count, `NINDIR()`, and last-group space.
- `init_resizeino()` creates `EXT2_RESIZEINO` using double-indirect blocks to point at reserved group descriptor backups.

Writing workflow:
- Allocates an anonymous mmap I/O buffer for superblock and group descriptors.
- In non-`Nflag` mode, writes the last sector to verify accessibility and zaps possible old ext2/UFS/LFS superblock magic at alternate locations.
- `initcg()` writes primary/backup superblocks and group descriptors where required, initializes block bitmaps, inode bitmaps, and inode tables with generation numbers.
- After `fsinit()`, writes final primary superblock/group descriptors.

Initial filesystem contents:
- `fsinit()` optionally initializes resize inode, creates `lost+found`, then creates root directory.
- Directory entries are written in little-endian form through `copy_dir()`.
- Root and `lost+found` inodes use current effective uid/gid and conventional modes.

Allocation and inode writes:
- `alloc()` allocates blocks from group 0, updates the block bitmap, group descriptor free counts, directory count, and superblock free block count.
- `iput()` writes an inode into its table, updates inode bitmap/free counts for non-reserved inodes, byte-swaps via ext2 helper routines, and converts block pointers to little endian.

I/O:
- `rdfs()` and `wtfs()` use sector-based offsets derived from `sectorsize`; `wtfs()` skips writes under `Nflag`.
- `uuid_get()` creates RFC4122 version 4 UUID bytes using `arc4random_buf()`.
