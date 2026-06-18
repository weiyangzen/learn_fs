# File Research: sources/os/linux/linux/fs/ntfs/object_id.c

Maintains `$Extend/$ObjId` index cleanup for NTFS object IDs.

Data structures:
- `object_id_index_key`: GUID key.
- `object_id_index_data`: file reference and birth/domain GUIDs.
- `object_id_index`: index entry layout for `$ObjId`.
- Global index name `objid_index_name` is `$O`.

Key flow:
- `open_object_id_index()` opens `FILE_Extend`, looks up `$ObjId`, opens its inode, and obtains the `$O` index context.
- `remove_object_id_index()` reads the existing `AT_OBJECT_ID` attribute GUID from the inode attribute stream and removes the matching index entry when found.
- `ntfs_delete_object_id_index()` opens the object-id attribute inode, opens the global object-id index, locks the index inode mrec, removes the entry, marks the index entry and MFT record dirty, and drops references.

Failure behavior:
- Missing object-id data returns `-ENODATA`.
- If `$ObjId` or its index cannot be opened, deletion silently does no index update and returns current `ret`.
- Uses `PTR_ERR()` from `ntfs_attr_iget()` when object-id attribute lookup fails.
