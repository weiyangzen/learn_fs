# File Research: sources/local-fs/ocfs2-tools/extras/compute_groups.c

Read coverage: complete file read, 79 lines.

Purpose: prints predicted OCFS2 group descriptor byte offsets for block-size and cluster-size combinations over a given device size.

Behavior:
- Optional argument overrides the default 2 TiB maximum size.
- Iterates block sizes from 512 bytes through 4096 bytes and cluster sizes from 4 KiB through 1 MiB.
- Uses `ocfs2_group_bitmap_size()` to compute clusters per group for each block size.
- Emits rows of byte offset, cluster-size string, and block-size string.

Dependencies: `libocfs2` group bitmap sizing helper and basic stdio/inttypes.

Risk notes:
- It is a calculation helper; it does not open or modify a filesystem.
- Input size is accepted via `strtoull()` without validation beyond conversion.
