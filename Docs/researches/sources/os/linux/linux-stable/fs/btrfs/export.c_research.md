# File Research: sources/os/linux/linux-stable/fs/btrfs/export.c

## Purpose
Implements Btrfs export operations for file handles, primarily for NFS/exportfs. It encodes inode/root/generation identity into file handles and reconstructs dentries or parent dentries across subvolume boundaries.

## File Handle Encoding
- `btrfs_encode_fh()` fills a packed `struct btrfs_fid`.
- Always records inode objectid, containing root objectid, and inode generation.
- If a parent is supplied, records parent objectid and generation.
- If parent and child live in different roots, records `parent_root_objectid` and returns `FILEID_BTRFS_WITH_PARENT_ROOT`.
- Supports three handle layouts:
  - `FILEID_BTRFS_WITHOUT_PARENT`
  - `FILEID_BTRFS_WITH_PARENT`
  - `FILEID_BTRFS_WITH_PARENT_ROOT`
- Returns `FILEID_INVALID` with the required `max_len` when the caller’s buffer is too small.

## Dentry Reconstruction
- `btrfs_get_dentry()` rejects internal objectids below `BTRFS_FIRST_FREE_OBJECTID`, gets the target root with `btrfs_get_fs_root()`, loads the inode with `btrfs_iget()`, verifies generation when non-zero, and returns `d_obtain_alias()`.
- `btrfs_fh_to_dentry()` validates file handle type/length and resolves the encoded inode.
- `btrfs_fh_to_parent()` validates parent-capable handle types and resolves either the child root or explicit parent root depending on handle type.

## Parent And Name Lookup
- `btrfs_get_parent()` finds the parent of a dentry by looking up the previous matching backref item:
  - For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for `BTRFS_ROOT_BACKREF_KEY`.
  - For normal inodes, it searches the subvolume root for `BTRFS_INODE_REF_KEY`.
  - It then returns the parent dentry, crossing roots when needed.
- `btrfs_get_name()` returns a child name under a parent:
  - Validates that the parent is a directory.
  - Uses `BTRFS_ROOT_BACKREF_KEY` for subvolume roots and `BTRFS_INODE_REF_KEY` for normal inodes.
  - Reads the name payload from the leaf into the exportfs buffer and null terminates it.

## Export Operations
`btrfs_export_ops` wires Btrfs into exportfs:
- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Dependencies
Uses root lookup and inode loading from `disk-io.c`/inode code, B-tree search via `btrfs_search_slot()`, and accessor helpers for inode/root backref items.
