# File Research: sources/os/linux/linux/fs/xfs/scrub/agino_bitmap.h

This header provides a small type-safe wrapper around `struct xbitmap32` for per-allocation-group inode numbers (`xfs_agino_t`). The wrapper type is `struct xagino_bitmap`, which contains one `xbitmap32` named `aginobitmap`.

The API consists of inline helpers to initialize, destroy, set, clear, test, and walk bitmap ranges: `xagino_bitmap_init`, `xagino_bitmap_destroy`, `xagino_bitmap_clear`, `xagino_bitmap_set`, `xagino_bitmap_test`, and `xagino_bitmap_walk`. Each helper forwards directly to the corresponding `xbitmap32` routine while preserving the semantic type of the start value as `xfs_agino_t`.

The main role in this group is supporting AGI unlinked-list repair in `agheader_repair.c`, where the repair code needs compact range tracking for per-AG inode numbers that are known or suspected to be unlinked. Keeping this as a wrapper prevents accidental mixing of AG block numbers, filesystem block numbers, and AG inode numbers while reusing the interval-tree backed 32-bit bitmap implementation.
