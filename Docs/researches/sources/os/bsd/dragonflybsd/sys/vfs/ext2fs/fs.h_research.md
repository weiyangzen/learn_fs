# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/fs.h

Provides ext2 filesystem constants and geometry macros adapted from UFS-style `fs.h`. It defines superblock size/location constants `SBSIZE`, `SBLOCK`, and byte offset `SBOFF`, plus `MAXMNTLEN`, `EXT2_MAXCONTIG`, and Orlov allocator tuning defaults `AFPDIR` and `AVGDIRSIZE`.

The key value of this header is address translation. `fsbtodb`, `dbtofsb`, `fsbtodoff`, `dofftofsb`, `dbtodoff`, `lblktodoff`, `lblktosize`, `lblkno`, and `blkoff` convert between filesystem blocks, disk blocks, byte offsets, and logical file blocks using precomputed fields in `struct m_ext2fs`.

Inode location macros map inode numbers to group/table locations. `ino_to_cg` selects the block group, `ino_to_fsba` locates the inode table block using `e2fs_gd_get_i_tables`, and `ino_to_fsbo` gives the inode index within the block.

Group mapping macros `dtog` and `dtogd` compute cylinder/block-group number and offset within group relative to `e2fs_first_dblock`.

Because ext2 in this implementation does not support fragments separately from blocks, `numfrags` and `blksize` are simple block-size operations, with `blksize` always returning `e2fs_fsize`.

Important dependencies: used by mount, vnode I/O, inode loading, block allocation/mapping, and directory logic. It depends on `EXT2_BLOCKS_PER_GROUP`, `EXT2_ADDR_PER_BLOCK`, and group descriptor accessors from other ext2 headers.

Notable risks or research hooks: the file preserves UFS terminology such as “cylinder group,” but ext2 uses block groups. Fragment-related macros assume no independent fragments, matching checks in `ext2_compute_sb_data`.
