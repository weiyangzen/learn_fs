# File Research: sources/os/linux/linux/fs/coda/cnode.c

Coda cnode/inode mapping helpers. This file maps Coda FIDs to Linux inodes, fills inode operations based on Coda vnode attributes, handles special control inode creation, and supports FID replacement.

Key functions:
- `coda_fideq()`: compares `struct CodaFid` objects byte-for-byte.
- `coda_fill_inode()`: applies Coda attributes and assigns inode/file operations for regular files, directories, symlinks, or special inodes.
- `coda_iget()`: obtains or creates an inode via `iget5_locked()` using Coda FID hash/test/set callbacks.
- `coda_cnode_make()`: fetches attributes from Venus, then calls `coda_iget()`.
- `coda_replace_fid()`: replaces an inode’s FID and rehashes it for disconnected-operation collision repair.
- `coda_fid_to_inode()`: looks up an existing inode by FID.
- `coda_ftoc()`: validates and returns Coda file private data.
- `coda_cnode_makectl()`: creates the special `.CONTROL` inode without Venus attributes.

Important behavior:
- `coda_iget()` retries if an existing inode has changed file type, removing it from hash and marking it purged.
- Symlink inodes use `page_get_link`, `coda_setattr`, no-highmem, and `coda_symlink_aops`.
- `coda_replace_fid()` contains a source comment noting locking is probably needed around in-place rehash.
