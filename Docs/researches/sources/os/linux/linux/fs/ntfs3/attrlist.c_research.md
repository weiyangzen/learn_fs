# File Research: sources/os/linux/linux/fs/ntfs3/attrlist.c

Read coverage: complete file, 428 lines.

This file manages ntfs3 in-memory and on-disk attribute lists, used when one MFT record cannot hold all attribute records for an inode.

Key functions:
- `al_destroy()` frees the attribute-list run and entry buffer and clears dirty/size state.
- `ntfs_load_attr_list()` loads `ATTR_LIST` from resident data or from nonresident runs using `run_unpack_ex()` and `ntfs_read_run_nb()`.
- `al_enumerate()` safely iterates list entries, checking size, bounds, and name storage.
- `al_find_le()` and `al_find_ex()` locate list entries by type, name, and optional VCN, respecting NTFS sort order.
- `al_add_le()` inserts a sorted list entry, grows backing storage, updates the on-disk `ATTR_LIST` size via `attr_set_size_ex()`, and writes nonresident lists immediately.
- `al_remove_le()` removes an entry and marks the list dirty.
- `al_update()` writes dirty list contents back to resident or nonresident storage and marks the owning MFT record dirty.

Integration:
- Used by `attrib.c`, inode record splitting, and multi-segment attribute handling.
- Depends on name comparison, runlist, attribute size, and MFT helpers.

Risks:
- Entry validation and sorted insertion are essential; corrupt sizes or offsets can otherwise walk outside the allocated list.
- `al_add_le()` mutates memory before resizing storage and must undo insertion correctly on failure.
- Dirty nonresident lists require explicit writeback to keep list entries and attribute segments synchronized.
