# File Research: sources/os/linux/linux-stable/fs/ntfs/object_id.h

`object_id.h` exposes object ID index maintenance to the rest of the NTFS driver.

Contents:
- Declares external Unicode index name `objid_index_name`.
- Declares `ntfs_delete_object_id_index(struct ntfs_inode *ni)`.

Design role:
- Small boundary header used by namespace/delete code to remove `$ObjId` entries without exposing object ID index internals.
