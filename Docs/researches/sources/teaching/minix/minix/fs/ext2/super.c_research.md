# File Research: sources/teaching/minix/minix/fs/ext2/super.c

This file reads, writes, and manages ext2 superblock and group descriptor state.

Key entry points:
- `get_super(dev)`: validates and returns the single mounted superblock.
- `get_block_size(dev)`: returns LMFS filesystem block size.
- `read_super(sp)`: reads superblock and group descriptor table, validates layout, derives in-memory fields, initializes search hints.
- `write_super(sp)`: writes superblock and dirty group descriptors.
- `get_group_desc(bnum)`: returns a group descriptor by group number.

Important behavior:
- Supports alternate superblock location through `opt.block_with_super`.
- Allocates on-disk and in-memory group descriptor arrays.
- Validates magic, block size, inode size, inode/block counts.
- Derives `s_block_size`, `s_blocksize_bits`, `s_max_size`, `s_inodes_per_block`, `s_itb_per_group`, `s_groups_count`, `s_gdb_count`, `s_desc_per_block`, `s_dirs_counter`, `s_bsearch`, and `s_igsearch`.
- Uses page-sized chunks for bdev reads/writes of descriptor table.

Endian handling:
- `super_copy()` and `gd_copy()` convert little-endian on non-little-endian CPUs, though runtime asserts little-endian in `main.c`.

Notable bug risk:
- `write_super()` calls `super_copy(ondisk_superblock, sp)` but then writes `(char *) sp` rather than `(char *) ondisk_superblock`; on big-endian this would bypass conversion.
