# File Research: sources/os/linux/linux/fs/ntfs/attrlist.c

Implements `$ATTRIBUTE_LIST` maintenance for NTFS inodes whose attributes span multiple MFT records.

Key entry points:
- `ntfs_attrlist_need()` checks whether an inode still needs an attribute list by scanning entries for references outside the base MFT record.
- `ntfs_attrlist_update()` writes the in-memory attribute-list buffer back to the `$ATTRIBUTE_LIST` attribute.
- `ntfs_attrlist_entry_add()` inserts a sorted attribute-list entry for a newly added attribute record.
- `ntfs_attrlist_entry_rm()` removes the entry referenced by an attribute search context.

Core mechanics:
- `ntfs_attrlist_need()` returns `1` when any list entry points at an extent MFT record, `0` when all entries are in the base record, and negative errno for invalid state.
- `ntfs_attrlist_update()` opens the `$ATTRIBUTE_LIST` attribute, truncates it to `base_ni->attr_list_size`, writes the in-memory buffer, updates `i_size`, and marks the base inode's list dirty.
- `ntfs_attrlist_update()` has a special `$MFT` recovery path: on `-ENOSPC` while updating `$MFT`'s attribute list, it truncates to zero and retries.
- `ntfs_attrlist_entry_add()` computes an aligned entry size, obtains the source MFT reference and sequence number, finds the sorted insertion point with `ntfs_attr_lookup()`, builds a new list buffer, swaps it into the base inode, and persists via `ntfs_attrlist_update()`.
- `ntfs_attrlist_entry_rm()` allocates a smaller buffer, copies around the removed entry, replaces the old list, and persists the new list.

Important invariants:
- Attribute-list entries are 8-byte aligned and sorted consistently with attribute lookup rules.
- Extent inodes redirect updates to their base inode when `ni->nr_extents == -1`.
- The in-memory `attr_list` and `attr_list_size` are changed only around an update call; add rolls back the pointer and size if persistence fails.

Notable risks:
- `ntfs_attrlist_entry_rm()` replaces `base_ni->attr_list` before `ntfs_attrlist_update()` succeeds, so a write failure leaves the in-memory list already modified.
- Entry validation is much lighter here than in `load_attribute_list()` and `ntfs_external_attr_find()`.
