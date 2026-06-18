# File Research: sources/os/bsd/freebsd-src/sbin/ffsinfo/ffsinfo.c

Implements `ffsinfo`, a diagnostic utility that dumps detailed UFS/FFS metadata for comparison before/after repair or growth operations.

Key responsibilities:
- Opens a UFS device with `libufs` and locates the superblock.
- Dumps selected metadata levels through debug macros from `growfs/debug.c`.
- Supports selecting a cylinder group, inode, detail level, and output file.
- Dumps primary and backup superblocks, cylinder summaries, cylinder groups, inode maps, fragment maps, cluster maps/summaries, inodes, and indirect block trees.

Options:
- `-g cylinder_group`: select one group; `-1` means last group; omitted means all.
- `-i inode`: dump a specific inode.
- `-l level`: bitmask controlling dump detail, valid `0x1` through `0x3ff`.
- `-o outfile`: debug output destination, default `-`.

Important data:
- `disk`: global `struct uufsd`.
- `fsun`: superblock scratch buffer.
- `i1blk`, `i2blk`, `i3blk`: buffers for indirect block traversal.
- `fscs`: allocated filesystem cylinder summary copy.

Detail-level behavior:
- `0x001`: primary superblock.
- `0x002`: backup superblocks.
- `0x004`: cylinder summaries.
- `0x008`, `0x010`, `0x020`, `0x040`: cylinder group and allocation maps.
- `0x100`: inode structures.
- `0x200`: direct/indirect block pointer traversal.

Inode dumping:
- `dump_whole_ufs1_inode()` and `dump_whole_ufs2_inode()` are parallel implementations for UFS1/UFS2 pointer sizes.
- Skip inodes with `di_nlink == 0`.
- Dump inode structure when requested.
- Follow single, double, and triple indirect blocks while accounting for remaining file blocks.

Risks and constraints:
- Diagnostic output depends on debug macros from growfs, not local formatting code.
- Indirect traversal assumes nonzero indirect block pointers when remaining blocks imply indirection; corrupted filesystems may cause read errors.
- In nested triple-indirect comments, the final formatted path uses `ind3ctr` twice where one field likely intended `ind2ctr`; this affects diagnostics only.
