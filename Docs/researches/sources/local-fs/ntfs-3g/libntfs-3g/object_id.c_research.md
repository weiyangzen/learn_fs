# File Research: sources/local-fs/ntfs-3g/libntfs-3g/object_id.c

## Purpose
Implements NTFS object ID extended attribute handling and `$Extend/$ObjId:$O` index maintenance.

## Main Interfaces
- `ntfs_get_ntfs_object_id()` reads object ID xattr data, merging index-stored birth/domain GUIDs when available.
- `ntfs_set_ntfs_object_id()` creates/replaces object ID data and index entry.
- `ntfs_remove_ntfs_object_id()` removes object ID attribute and index entry.
- `ntfs_delete_object_id_index()` removes only the index entry for an existing attribute.
- Internal helpers open `$ObjId`, add/remove/update index entries, merge index data, and create a dummy attribute.

## Control Flow
The on-file `$OBJECT_ID` attribute stores only the object GUID. The `$ObjId` index stores GUID key to file reference plus birth volume/object/domain GUIDs. Setting first opens `$Extend/$ObjId`, checks uniqueness unless the existing entry belongs to the same inode, adds the attribute if allowed by xattr flags, removes any old index entry, truncates/writes the GUID attribute, and inserts the full index entry.

Removal removes the index first, then removes the attribute; if attribute removal fails after index removal, it attempts to restore the index and logs possible corruption.

## Integration Points
Uses `ntfs_inode_open()`, `ntfs_inode_lookup_by_mbsname()`, `ntfs_index_ctx_get()`, `ntfs_index_lookup()`, `ntfs_ie_add()`, `ntfs_index_rm()`, attribute read/write/truncate/remove helpers, and xattr flag semantics.

## Risks and Invariants
- GUID indexing uses Windows-compatible little-endian comparison semantics.
- NTFS version must be at least 3 for adding object ID attributes.
- Partial failure can leave object ID/index inconsistency; code attempts repair and logs possible corruption.
- `ntfs_get_ntfs_object_id()` treats unexpected attribute sizes as unsupported.
