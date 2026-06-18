# File Research: sources/os/linux/linux-stable/fs/ntfs/attrlist.h

Purpose: Header exporting attribute-list maintenance APIs.

Exports:
- `ntfs_attrlist_need()`
- `ntfs_attrlist_entry_add()`
- `ntfs_attrlist_entry_rm()`
- `ntfs_attrlist_update()`

Dependencies:
- Includes `attrib.h`, because APIs use `struct ntfs_attr_search_ctx`, `struct ntfs_inode`, and `struct attr_record`.

Role in subsystem:
- This is the narrow bridge from core attribute mutation code to `$ATTRIBUTE_LIST` persistence.
