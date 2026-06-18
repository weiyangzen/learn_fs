# File Research: sources/teaching/os161/kern/fs/sfs/sfs_dir.c

Implements SFS directory entry I/O and directory lookup/link/unlink helpers.

Key behavior:
- Directory entries are fixed-size `struct sfs_direntry` records stored in directory file data.
- `sfs_readdir` and `sfs_writedir` translate slot numbers to byte offsets and use `sfs_metaio`.
- `sfs_dir_nentries` validates directory size is a multiple of entry size.
- `sfs_dir_findname` scans all slots, reports found inode/slot, and optionally reports an empty slot (`SFS_NOINO`).
- `sfs_dir_link` ensures the name does not exist, checks `SFS_NAMELEN`, reuses an empty slot or appends, and writes the new entry.
- `sfs_dir_unlink` clears a slot by writing `SFS_NOINO`.
- `sfs_lookonce` finds a name, loads its vnode, and panics if a directory entry points to an inode with zero link count.

Notable design:
- Directories are simple linear arrays with no hashing and no subdirectory-specific logic here.
- `sfs_dir_findname` asserts duplicate names do not occur.
