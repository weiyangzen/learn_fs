# File Research: sources/os/linux/linux-stable/fs/exfat/exfat_fs.h

This is the central internal header for the exFAT driver. It defines in-memory filesystem structures, internal type constants, conversion macros, inline helpers, and cross-file function prototypes.

Key elements:
- Defines internal `TYPE_*` values for raw dentry categories, plus entry-set constants such as `ES_IDX_FILE`, `ES_IDX_STREAM`, and `ES_IDX_FIRST_FILENAME`.
- Provides byte/cluster/block/dentry conversion macros, FAT entry offset macros, allocation bitmap offset macros, and entry-set size limits.
- Defines `struct exfat_mount_options`, including uid/gid masks, charset options, error behavior, discard, timezone behavior, trailing-dot handling, and zero-size directory support.
- Defines `struct exfat_sb_info`, which stores geometry, FAT/data starts, root directory cluster, bitmap buffers, upcase table, used cluster count, locks, NLS table, inode hash table, and options.
- Defines `struct exfat_inode_info`, extending VFS inode state with exFAT directory location, entry index, raw attributes, start cluster, allocation flags, lookup/allocation hints, cluster cache state, on-disk position, valid size, and truncate lock.
- Provides inline helpers for `EXFAT_SB()`, `EXFAT_I()`, forced shutdown checks, mode/attribute conversion, cluster/sector conversion, cluster validity, and chain walking/advancing.

Important dependencies:
- Included by every exFAT implementation file in this group.
- Raw on-disk layout comes from `exfat_raw.h`.
- Prototypes expose the module boundaries between allocation, FAT, file operations, name operations, cache, directory, inode, NLS, and misc utilities.

Critical contracts:
- `ALLOC_NO_FAT_CHAIN` means clusters are physically contiguous and can be walked arithmetically; `ALLOC_FAT_CHAIN` requires FAT lookup.
- `valid_size` is tracked separately from logical `i_size` to preserve exFAT valid-data-length semantics.
- `s_lock` serializes broad filesystem metadata operations; `bitmap_lock` serializes bitmap allocation/free; inode `truncate_lock` protects bmap against truncate.
