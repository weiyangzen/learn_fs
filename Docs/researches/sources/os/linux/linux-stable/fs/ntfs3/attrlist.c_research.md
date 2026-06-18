# File Research: sources/os/linux/linux-stable/fs/ntfs3/attrlist.c

This file manages ntfs3 `$ATTRIBUTE_LIST` data for inodes whose attributes span multiple MFT records or segments.

Main responsibilities:
- Loads resident or nonresident attribute-list contents into `ni->attr_list`.
- Enumerates and validates variable-sized `ATTR_LIST_ENTRY` records.
- Finds entries by attribute type, name, and VCN.
- Inserts new list entries in NTFS sorted order.
- Removes list entries and marks the list dirty.
- Persists dirty attribute-list content back to resident data or nonresident runs.

Important functions:
- `al_destroy()` frees the list run and entry buffer and resets dirty/size state.
- `ntfs_load_attr_list()` handles resident copy or nonresident run unpack plus read into a kvmalloc buffer.
- `al_enumerate()` validates bounds, size, and name offset before returning the next entry.
- `al_find_le()` and `al_find_ex()` locate the matching or preceding list entry for a VCN.
- `al_add_le()` grows the in-memory list, inserts a sorted entry, resizes `$ATTRIBUTE_LIST` through `attr_set_size_ex()`, and writes nonresident list data if needed.
- `al_remove_le()` removes an entry by memmove after validating it belongs to the current list.
- `al_update()` shrinks or writes the backing `$ATTRIBUTE_LIST` attribute and clears the dirty flag.

Research notes:
- The code assumes list entries are sorted by type, name, and VCN; lookup and insertion depend on that invariant.
- Nonresident list loading comments estimate worst-case memory at about 16 MiB for extremely fragmented 1 TiB files with 4 KiB clusters.
