# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.h

This header defines the on-disk/in-core layout and public interface for JFS directory B+-tree pages.

Key responsibilities:
- Defines `ddata_t`, the insert payload union for leaf entries (`tid`, inode pointer, inode number) or internal entries (`pxd_t` child extent).
- Defines 32-byte directory slots (`struct dtslot`) and type-specific head slots for internal entries (`struct idtentry`) and leaf entries (`struct ldtentry`).
- Defines slot-size constants and macros for computing the number of slots needed for internal, modern leaf, and legacy leaf entries.
- Defines the persistent directory-table slot format (`struct dir_table_slot`) and helpers to pack/unpack 40-bit page addresses or deleted-entry forward links.
- Defines the inline directory root (`dtroot_t`) stored in the inode and the external directory page (`dtpage_t`) used after the directory grows.
- Provides helper macros for parent inode lookup, empty-directory checks, sorted-entry table access, and directory-end offsets.
- Declares the dtree API: root initialization, search, insert, delete, modify, readdir, and page/root validators.

Important interactions:
- Included by `jfs_incore.h`, which embeds `dtroot_t` and the inline directory table in `struct jfs_inode_info`.
- Depends on generic JFS B+-tree and extent descriptor definitions from `jfs_btree.h`.
- Exposes `JFS_CREATE`, `JFS_LOOKUP`, `JFS_REMOVE`, and `JFS_RENAME` operation codes consumed by `dtSearch()`.

Notable invariants and risks:
- Inline roots have only 9 slots, while regular pages have 128 slots; code must select the correct sorted-table location with `DT_GETSTBL()`.
- Directory-table entries have two meanings for `addr2`: low address bits for valid entries, or next-index links for free/deleted entries.
- The `DO_INDEX()` macro changes leaf-entry capacity and traversal behavior; mixed handling of legacy and indexed directories is a recurring source of subtle offset and slot-count logic.

Research notes:
- This header is the compact schema for the dtree manager. It explains why `jfs_dtree.c` is dominated by slot accounting, sorted-table shifting, and format compatibility checks.
