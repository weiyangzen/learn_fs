# File Research: sources/os/linux/linux-stable/fs/ocfs2/export.c

Purpose: Implements OCFS2 NFS/exportfs support by encoding file handles, resolving handles back to dentries, and locating directory parents.

Read coverage: complete file read, 285 lines.

Key structures and state:
- `struct ocfs2_inode_handle` stores an inode block number and generation.
- File handles encode child block number high/low words plus generation, optionally followed by parent block number high/low words plus generation.

Major logic:
- `ocfs2_get_dentry()` resolves a handle by first checking the inode cache, then taking the NFS sync lock, verifying the inode allocator bit, igetting the inode, and checking generation.
- `ocfs2_get_parent()` takes the NFS sync lock and directory metadata lock, resolves `".."`, validates the parent inode allocator bit, and returns an alias dentry.
- `ocfs2_encode_fh()` emits three 32-bit words for a non-connectable handle and six words when a parent inode is supplied.
- `ocfs2_fh_to_dentry()` and `ocfs2_fh_to_parent()` decode little-endian handle words into `ocfs2_inode_handle` values.
- Exports `ocfs2_export_ops` for VFS exportfs integration.

Concurrency and lifetime:
- The NFS sync lock serializes handle resolution against inode deletion across cluster nodes.
- Directory parent lookup also holds the directory inode lock while reading `".."`.
- Resolved inodes are returned through `d_obtain_alias()`; stale or generation-mismatched handles return `-ESTALE`.

Important dependencies:
- Uses inode lookup/iget, inode allocator bit tests, directory name lookup, dentry aliasing, DLM NFS sync lock wrappers, and exportfs operations.

Risk notes:
- Handle validity depends on both allocator-bit state and generation matching.
- Parent lookup maps several lower-level invalid-inode cases to `-ESTALE` or `-ENOENT` to fit NFS expectations.
