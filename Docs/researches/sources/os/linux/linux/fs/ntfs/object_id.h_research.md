# File Research: sources/os/linux/linux/fs/ntfs/object_id.h

Header for object-id index support.

Exports:
- `objid_index_name`.
- `ntfs_delete_object_id_index()`.

Role:
- Used by deletion paths to remove stale `$Extend/$ObjId` index entries when an inode with `AT_OBJECT_ID` loses its last link.
