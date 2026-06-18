# File Research: sources/os/linux/linux-stable/fs/ntfs/attrlist.c

Purpose: Maintains NTFS `$ATTRIBUTE_LIST` contents for files whose attributes span multiple MFT records.

Key responsibilities:
- `ntfs_attrlist_need()` decides whether an inode still needs an attribute list by checking whether any list entry references an MFT record other than the base inode.
- `ntfs_attrlist_update()` opens the `$ATTRIBUTE_LIST` attribute, resizes it to `base_ni->attr_list_size`, writes the in-memory list to disk, handles a special `$MFT` ENOSPC retry path, and marks attrlist state dirty.
- `ntfs_attrlist_entry_add()` allocates a larger in-memory attrlist, finds the sorted insertion point using attribute lookup, builds a new `struct attr_list_entry`, copies old entries around it, updates `base_ni->attr_list`, and persists via `ntfs_attrlist_update()`.
- `ntfs_attrlist_entry_rm()` removes the current `ctx->al_entry` from the base inode’s in-memory attrlist and persists the resized list.

Important invariants:
- Attribute-list entries are sorted according to the same lookup/collation rules used by `ntfs_attr_lookup()`.
- Entry length is 8-byte aligned and includes any Unicode name payload.
- `mft_reference` uses the containing MFT record number and sequence number.
- If the update fails after add, the old list pointer and size are restored.

Dependencies:
- Uses `attrib.c` lookup/truncate/write paths to find insertion points and persist the list.
- Uses `mft.h` for MFT mapping and sequence-number reference construction.

Risk notes:
- `ntfs_attrlist_need()` assumes valid in-memory list entry lengths; corruption validation is handled elsewhere.
- `ntfs_attrlist_entry_rm()` replaces the list before calling `ntfs_attrlist_update()`, so persistence failure leaves the in-memory list already modified.
