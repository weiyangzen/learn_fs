# File Research: sources/os/linux/linux-stable/fs/hfs/inode.c

## Scope

Implements classic HFS inode lifecycle, address-space operations, fork read/write, inode writeback, resource-fork lookup, setattr/truncate, fsync, and file operation tables.

## APIs And Behavior

- Address-space methods map buffered/direct I/O through `hfs_get_block()`, clean up failed extending writes, and release cached bnodes from B-tree pages when possible.
- `hfs_new_inode()` allocates a VFS inode, assigns a CNID from `next_id`, initializes mode/ownership/extent state, updates file/folder/root counters, and marks the MDB dirty.
- `hfs_delete_inode()` decrements counters and truncates regular files with no links.
- `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate between on-disk fork extent/size fields and in-memory extent/size state.
- `hfs_iget()` uses `iget5_locked()` with catalog record matching to load files or directories.
- `hfs_write_inode()` flushes dirty extents, writes B-tree headers for special tree inodes, and updates catalog file/folder records for normal and resource-fork inodes.
- `hfs_file_lookup()` exposes the resource fork as a synthetic `rsrc` child inode of regular file inodes.
- `hfs_inode_setattr()` restricts uid/gid/mode changes to HFS' model and performs size changes through `hfs_file_truncate()`.
- `hfs_file_fsync()` writes data, writes the inode/MDB, flushes delayed MDB work, and syncs the block device.

## State And Dependencies

This file ties VFS inode/page-cache operations to catalog and extent metadata. It depends on catalog lookup keys, extent allocation/truncation, MDB dirty delayed work, xattrs, generic file helpers, and the B-tree special inodes.

## Risks And Invariants

HFS permissions are coarse: file write bits are all-on or all-off and directories cannot meaningfully change mode beyond the mount mask. Resource fork inodes are fake-hashed and share catalog records with their main inode, so writeback routes through `main_inode`. B-tree page release must not free a referenced bnode.
