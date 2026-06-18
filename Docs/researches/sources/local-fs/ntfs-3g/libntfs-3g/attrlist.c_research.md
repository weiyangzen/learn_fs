# File Research: sources/local-fs/ntfs-3g/libntfs-3g/attrlist.c

## Scope

Manages `$ATTRIBUTE_LIST` contents for inodes whose attributes span multiple MFT records.

## API And Behavior

- `ntfs_attrlist_need()` checks whether any attribute-list entry points outside the base inode MFT reference; if all entries point to the base record, the attribute list is no longer needed.
- `ntfs_attrlist_entry_add()` creates an aligned `ATTR_LIST_ENTRY` from an `ATTR_RECORD`, finds the sorted insertion point using `ntfs_attr_lookup()`, resizes the `$ATTRIBUTE_LIST` attribute, builds a new in-memory list buffer, inserts the entry, swaps it into `ni->attr_list`, updates `attr_list_size`, and marks the list dirty.
- `ntfs_attrlist_entry_rm()` removes `ctx->al_entry` from the base inode attribute list, resizes `$ATTRIBUTE_LIST`, copies all remaining entries into a new buffer, replaces `base_ni->attr_list`, and marks the list dirty.

## State And Dependencies

The file depends on `ntfs_inode` base/extent relationships, `ATTR_LIST_ENTRY`, `ATTR_RECORD`, attribute search contexts, `ntfs_attr_open()`, `ntfs_attr_truncate()`, and dirty tracking through `NInoAttrListSetDirty()`.

## Risks And Invariants

Attribute-list entries must remain sorted and 8-byte aligned. The code assumes existing in-memory list entries are well formed when iterating by `length`; corrupt lengths can break traversal. Add/remove operations resize the on-disk `$ATTRIBUTE_LIST` first and then replace the in-memory buffer, so errors after resize are sensitive and rely on callers/filesystem repair paths to recover.
