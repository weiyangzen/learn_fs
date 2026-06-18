# File Research: sources/local-fs/kdave-linux/fs/btrfs/export.c

## Role

Implements Btrfs `export_operations` for NFS/exportfs-style file handles. It encodes Btrfs inode and root identity into file handles, decodes file handles back to dentries, finds parent dentries, and resolves child names from parent/child dentries across ordinary subvolume files and subvolume root entries.

## File Handle Encoding

- `BTRFS_FID_SIZE_NON_CONNECTABLE`, `BTRFS_FID_SIZE_CONNECTABLE`, and `BTRFS_FID_SIZE_CONNECTABLE_ROOT` describe file-handle sizes in 32-bit words.
- `btrfs_encode_fh()` writes:
  - inode object ID;
  - root object ID;
  - inode generation;
  - optional parent object ID and generation;
  - optional parent root object ID when parent and child live in different roots.
- It returns `FILEID_BTRFS_WITHOUT_PARENT`, `FILEID_BTRFS_WITH_PARENT`, `FILEID_BTRFS_WITH_PARENT_ROOT`, or `FILEID_INVALID` when the caller's buffer is too small.

## File Handle Decoding

- `btrfs_get_dentry()` validates object IDs, gets the target root by root object ID, loads the inode with `btrfs_iget()`, verifies generation when provided, and returns `d_obtain_alias()` for the inode.
- `btrfs_fh_to_dentry()` validates file-handle type/length, extracts object ID, root ID, and generation, then delegates to `btrfs_get_dentry()`.
- `btrfs_fh_to_parent()` handles only parent-bearing file-handle types, selects either the child's root ID or explicit parent root ID, and delegates to `btrfs_get_dentry()` for the parent object.

## Parent and Name Lookup

- `btrfs_get_parent()` handles two cases:
  - For a subvolume root inode (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for a `BTRFS_ROOT_BACKREF_KEY` and returns the containing directory in the parent root.
  - For an ordinary inode, it searches the current root for the previous `BTRFS_INODE_REF_KEY` and returns the referenced parent inode.
- The function treats an exact key with offset `-1` as corruption (`-EUCLEAN`) because such an inode/root ID should not exist.
- `btrfs_get_name()` resolves the name of `child` under `parent`. It rejects non-directory parents, then reads either:
  - a `BTRFS_ROOT_BACKREF_KEY` name for subvolume root entries; or
  - a `BTRFS_INODE_REF_KEY` name for ordinary inode references.
- It copies the name from the leaf item payload and appends a null terminator for exportfs reconnect path handling.

## Export Operations

`btrfs_export_ops` wires:

- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Dependencies

Uses VFS/exportfs interfaces, Btrfs inode helpers, root lookup through `disk-io.h`, tree search/accessor helpers, superblock access, and Btrfs root/inode reference item formats.

## Research Notes

The key Btrfs-specific export complexity is that inode numbers are only unique inside a root/subvolume. File handles must include root identity, and connectable file handles may need the parent's root identity too. Subvolume roots are represented through root backrefs rather than ordinary inode refs, so both parent and name lookup have dedicated subvolume-root branches.
