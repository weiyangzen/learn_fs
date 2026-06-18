# File Research: sources/os/linux/linux-stable/fs/affs/inode.c

This file translates AFFS on-disk header blocks into Linux inodes, writes inode metadata back, creates new inodes, evicts inodes, handles setattr, and inserts directory entries.

Major responsibilities:
- `affs_iget()` reads a header block, validates checksum/type, initializes AFFS-private inode state, maps Amiga permissions and ownership, and assigns VFS operation tables by secondary type.
- `affs_write_inode()` writes protection, size, UID/GID, and timestamps back to AFFS tail or root-tail fields.
- `affs_setattr()` enforces mount-option restrictions, handles truncate-on-size-change, copies attributes, and converts Linux mode back to Amiga protection bits.
- `affs_evict_inode()` truncates deleted files, syncs metadata for live files, releases extension caches, releases cached extension blocks, frees preallocation, and frees the inode header block on last unlink.
- `affs_new_inode()` allocates a disk block, creates a VFS inode, initializes AFFS private state, and inserts it into the inode hash.
- `affs_add_entry()` initializes a header or link block and inserts it into the parent directory hash table.

Inode decoding:
- Directories receive `affs_dir_inode_operations` and `affs_dir_operations`.
- Regular files receive `affs_file_inode_operations`, `affs_file_operations`, and either `affs_aops` or `affs_aops_ofs`.
- Symlinks receive `affs_symlink_inode_operations` and `affs_symlink_aops`.
- `ST_LINKFILE` entries resolve through `original`; `ST_LINKDIR` is treated as a directory-like inode without full operation setup.
- MUFS UID/GID translation handles `0xffff` specially for root.

Directory entry insertion:
- Hard links allocate a separate link block, set `original`, splice it into the original inode’s `link_chain`, and force the VFS nlink to two.
- New header blocks receive `T_SHORT`, key, AFFS name, secondary type, parent pointer, checksum, and metadata dirty tracking.
- The dentry stores the actual header block number in `d_fsdata`.
- Parent hash insertion is serialized by `affs_lock_dir()`; link-chain updates use `affs_lock_link()`.
