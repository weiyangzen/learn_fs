# File Research: sources/os/linux/linux-stable/fs/coda/cnode.c

## Purpose
Implements Coda inode creation, lookup by Coda FID, inode operation selection, FID replacement, and control inode creation.

## Main Interfaces
- Inode creation/lookup: `coda_iget()`, `coda_cnode_make()`, `coda_fid_to_inode()`.
- FID management: `coda_replace_fid()`.
- File private access: `coda_ftoc()`.
- Control inode: `coda_cnode_makectl()`.

## Control Flow
`coda_cnode_make()` asks Venus for attributes with `venus_getattr()` and then calls `coda_iget()`. `coda_iget()` uses `iget5_locked()` with a hash derived from the FID, sets `i_ino`, initializes `coda_inode_info`, and calls `coda_fill_inode()` for new inodes. If an existing inode’s type no longer matches Venus attributes, it removes the inode from the hash, flags it for purge, drops it, and retries.

`coda_fill_inode()` translates Coda attributes to VFS inode attributes and installs file, directory, symlink, or special inode operations. Symlinks use page symlink operations and `coda_symlink_aops`.

`coda_replace_fid()` handles the special disconnected-create case where a local FID is replaced by a globally unique one by removing and reinserting the inode hash with the new FID-derived inode number.

## State And Synchronization
Inode identity is stored in `coda_inode_info.c_fid` and is normally immutable. The FID replacement path notes a lock concern in comments, making it a sensitive area.

## Integration Points
Used by directory lookup/create/mkdir and by downcall paths that need to map a Venus FID back to a VFS inode.

## Risks And Review Focus
- FID collisions and replacement can confuse inode hashing and in-flight upcalls.
- Type changes from Venus force inode purge/retry, which can affect dentries holding old type assumptions.
