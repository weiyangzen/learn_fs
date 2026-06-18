# File Research: sources/local-fs/btrfs-linux/fs/btrfs/export.c

## Summary
Implements Btrfs exportfs/NFS file-handle encoding and decoding, including subvolume-aware parent lookup and name reconstruction.

## Main Responsibilities
- Encode Btrfs inode identity into export file handles.
- Include parent inode and parent root identity when a connectable handle is requested.
- Decode file handles back to dentries.
- Decode parent file handles.
- Locate a child’s parent dentry.
- Recover a child name under a parent for exportfs reconnect paths.

## Key APIs
- `btrfs_encode_fh()`
- `btrfs_get_dentry()`
- `btrfs_fh_to_dentry()`
- `btrfs_fh_to_parent()`
- `btrfs_get_parent()`
- `btrfs_get_name()`
- `btrfs_export_ops`

## Important Behavior
File handles store objectid, root objectid, and inode generation. Connectable handles additionally store parent objectid and parent generation. If the parent is in a different subvolume root, the handle also stores `parent_root_objectid` and uses the `FILEID_BTRFS_WITH_PARENT_ROOT` type.

`btrfs_get_dentry()` rejects objectids below `BTRFS_FIRST_FREE_OBJECTID`, obtains the requested root with `btrfs_get_fs_root()`, loads the inode with `btrfs_iget()`, verifies generation when provided, and returns an alias dentry.

`btrfs_get_parent()` handles two cases. For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for a `BTRFS_ROOT_BACKREF_KEY`. For normal inodes, it searches the current root for the previous `BTRFS_INODE_REF_KEY`. It then returns either the parent directory inode in the same root or a dentry from the parent root.

`btrfs_get_name()` reconstructs the child name from either root backrefs or inode refs and writes a NUL terminator for exportfs path reconnect logic.

## State and Dependencies
The implementation depends on Btrfs root references, inode lookup, tree searches, inode refs, root backrefs, and extent-buffer accessors. It is wired into VFS exportfs through `const struct export_operations btrfs_export_ops`.

## Risks
Subvolume boundaries are the main correctness risk. Handles must distinguish parent roots when parent and child are not in the same root, or exportfs can reconnect to the wrong directory.

Generation checks protect against stale handles; bypassing them would risk resolving a reused inode number as the wrong file.

`btrfs_get_parent()` relies on finding the immediately preceding backref/ref item after a search for offset `-1`; corruption or unexpected key ordering returns `-EUCLEAN` or `-ENOENT`.
