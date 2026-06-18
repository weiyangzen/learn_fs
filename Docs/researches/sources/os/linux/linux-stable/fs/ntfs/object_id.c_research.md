# File Research: sources/os/linux/linux-stable/fs/ntfs/object_id.c

`object_id.c` handles deletion of NTFS object ID index entries from `$Extend/$ObjId`.

Key structures:
- `object_id_index_key` wraps an object GUID key.
- `object_id_index_data` stores file ID, birth volume ID, birth object ID, and domain ID.
- `object_id_index` models a full `$ObjId` index entry.
- `objid_index_name` is the Unicode `$O` index name.

Key functions:
- `open_object_id_index()` opens `$Extend`, looks up `$ObjId`, opens its inode, and returns an index context for `$O`.
- `remove_object_id_index()` reads the inode’s `AT_OBJECT_ID` value, looks it up in the object ID index, and removes the matching index entry if present.
- `ntfs_delete_object_id_index()` opens the target object-id attribute inode, opens the global object ID index, locks the index inode MFT record, removes the entry, marks the index entry and MFT record dirty on success, and releases references.

Dependencies:
- Directory lookup via `ntfs_lookup_inode_by_name()`.
- Attribute inode access via `ntfs_attr_iget()`.
- Index lookup/removal via `ntfs_index_lookup()` and `ntfs_index_rm()`.
- Dirtying via `ntfs_index_entry_mark_dirty()` and `mark_mft_record_dirty()`.

Behavioral role:
- Called by namespace deletion when final link removal needs associated object ID metadata unindexed.
