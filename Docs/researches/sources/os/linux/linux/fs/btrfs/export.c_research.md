# File Research: sources/os/linux/linux/fs/btrfs/export.c

## Purpose

`export.c` implements Btrfs export operations for file handles, primarily for NFS/exportfs support. It encodes Btrfs inode/root identities into stable file handles and decodes those handles back into dentries, parents, and names across subvolumes.

## File Handle Encoding

`btrfs_encode_fh()` fills `struct btrfs_fid` with:

- inode objectid
- root objectid
- inode generation
- optional parent objectid
- optional parent generation
- optional parent root objectid when the parent is in a different subvolume/root

It returns one of the Btrfs file-handle types:

- `FILEID_BTRFS_WITHOUT_PARENT`
- `FILEID_BTRFS_WITH_PARENT`
- `FILEID_BTRFS_WITH_PARENT_ROOT`

If the caller-provided buffer is too small, it updates `max_len` and returns `FILEID_INVALID`.

## Dentry Reconstruction

`btrfs_get_dentry()` reconstructs a dentry from `objectid`, `root_objectid`, and optional generation:

1. Rejects reserved object IDs below `BTRFS_FIRST_FREE_OBJECTID`.
2. Gets the root via `btrfs_get_fs_root()`.
3. Looks up the inode via `btrfs_iget()`.
4. Validates generation if nonzero.
5. Returns an alias dentry via `d_obtain_alias()`.

`btrfs_fh_to_dentry()` decodes the inode identity from a file handle and calls `btrfs_get_dentry()`.

`btrfs_fh_to_parent()` decodes parent identity, including cross-root parent handles, and calls `btrfs_get_dentry()`.

## Parent Lookup

`btrfs_get_parent()` finds a child dentry’s parent:

- For subvolume roots (`BTRFS_FIRST_FREE_OBJECTID`), it searches the tree root for `BTRFS_ROOT_BACKREF_KEY`.
- For regular inodes, it searches the inode’s root for `BTRFS_INODE_REF_KEY`.
- It walks to the previous matching key after a search with offset `-1`.
- It returns either a parent dentry in another root or a parent inode alias in the same root.

## Name Lookup

`btrfs_get_name()` resolves a child name relative to a parent dentry:

- Verifies the parent is a directory.
- For subvolume roots, reads the name from `BTRFS_ROOT_BACKREF_KEY`.
- For regular inodes, reads the name from `BTRFS_INODE_REF_KEY`.
- Copies the stored name from the leaf and NUL-terminates it for exportfs reconnect logic.

## Export Operations

`btrfs_export_ops` wires Btrfs into exportfs:

- `.encode_fh = btrfs_encode_fh`
- `.fh_to_dentry = btrfs_fh_to_dentry`
- `.fh_to_parent = btrfs_fh_to_parent`
- `.get_parent = btrfs_get_parent`
- `.get_name = btrfs_get_name`

## Integration Points

The file depends on root lookup from `disk-io.c`, inode lookup from Btrfs inode code, key search from the Btrfs tree API, and exportfs from the VFS.

## Risks and Invariants

- Generation checks protect against stale file handles.
- Cross-subvolume parent handles require `parent_root_objectid`.
- Reserved object IDs are rejected as stale.
- Parent/name lookup assumes Btrfs backref items are present and structurally valid.
