# File Research: sources/os/linux/linux/fs/jfs/jfs_dtree.h

## Role

Defines the on-disk/in-memory directory tree layout and public directory B+tree API used by JFS directory operations.

## Key Responsibilities

- Defines directory slot formats: generic continuation `dtslot`, internal/router `idtentry`, and leaf `ldtentry`.
- Defines slot sizing constants and macros for computing how many slots a leaf or internal entry needs.
- Defines persistent directory index support through `struct dir_table_slot`, validity flags, and address packing/unpacking macros.
- Defines the inline directory root `dtroot_t`, including DASD data, parent inode number, freelist state, and inline sorted-entry table.
- Defines external directory page `dtpage_t`, including sibling links, page flags, freelist state, max slot count, stbl location, and self extent descriptor.
- Provides constants for supported directory page sizes, table-slot counts, entry start offsets, and maximum directory offset sentinel.
- Defines `DT_GETSTBL()` to locate the sorted-entry table for inline roots versus external pages.
- Exposes search-operation flags: `JFS_CREATE`, `JFS_LOOKUP`, `JFS_REMOVE`, and `JFS_RENAME`.
- Declares public dtree entry points for root init, search, insert, delete, modify, readdir, and page validation.

## Important Interactions

- Included by `jfs_incore.h`, which embeds `dtroot_t` and inline directory table storage into `struct jfs_inode_info`.
- Depends on `jfs_btree.h` for common B+tree flags and transaction stack structures.
- `DO_INDEX()` depends on the superblock mount flag `JFS_DIR_INDEX`, defined in `jfs_filsys.h`.
- `PARENT()` reads the parent directory inode number from the inline root header.

## Invariants and Risks

- Slot sizes and data-length constants must match the on-disk JFS directory format exactly.
- Legacy leaf entries use 13 UTF-16 characters in the head segment; indexed directories use 11 plus a 32-bit persistent index field.
- External page `stblindex` divides page slots into entry data and sorted-index table regions.
- `dtroot_t` reserves slot 0 for the header overlay; usable inline root slots start at `DTENTRYSTART`.
