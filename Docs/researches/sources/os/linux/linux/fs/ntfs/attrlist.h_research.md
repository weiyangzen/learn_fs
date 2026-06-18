# File Research: sources/os/linux/linux/fs/ntfs/attrlist.h

Declares the small `$ATTRIBUTE_LIST` maintenance API used by attribute mutation code.

Exports:
- `ntfs_attrlist_need()` tests whether a base inode still requires an attribute list.
- `ntfs_attrlist_entry_add()` adds a list entry for an attribute record.
- `ntfs_attrlist_entry_rm()` removes the list entry described by a search context.
- `ntfs_attrlist_update()` persists the base inode's in-memory attribute-list buffer.

Integration:
- Includes `attrib.h` because removal is keyed by `struct ntfs_attr_search_ctx`.
- Used by `attrib.c` when adding, deleting, moving, and rewriting attribute records.

Notable risks:
- The header exposes no locking contract; callers must follow the surrounding attribute/MFT locking discipline.
