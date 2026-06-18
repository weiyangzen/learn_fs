# File Research: sources/os/linux/linux-stable/fs/afs/dir.c

This file implements AFS directory reading, validation, lookup, dentry revalidation, create/link/symlink/mkdir/unlink/rmdir/rename operations, directory cache writeback, and dentry lifecycle hooks.

Major responsibilities:
- Defines AFS directory file, inode, address-space, and dentry operations.
- Reads whole directories synchronously into folio-queue buffers.
- Validates 2 KiB AFS directory blocks and iterates entries using bitmap slot allocation.
- Performs local directory search and server-side status fetches for lookup.
- Uses inline bulk status where available to prefetch neighboring lookup targets.
- Revalidates dentries against directory data-version changes and invalidation windows.
- Implements mutating directory operations through `struct afs_operation` dispatch to AFS/YFS RPC clients.
- Applies local directory blob edits after successful mutations when data-version deltas match.
- Handles silly rename for busy unlink/rename targets.

Directory read model:
- AFS directories are read as a single unit to avoid inconsistent contents across partial reads.
- `afs_read_dir()` uses `validate_lock` and reloads only when directory contents are invalid or unread.
- Directory size must be at least one block and no more than 1024 directory blocks.
- `afs_dir_check()` verifies magic in each block and NUL-terminates block data so string functions are bounded.
- Directory iteration rounds positions to dirent boundaries and then walks folio queues block by block.

Lookup:
- `afs_do_lookup()` first searches the cached directory by hash using `afs_dir_search()`.
- The found FID is used to locate an existing inode or to fetch status from the server.
- If the callback server supports inline bulk status, the code scans ahead up to 50 FIDs and fetches statuses in one operation.
- The primary looked-up inode is returned; speculative neighbors may be instantiated or updated.
- `@sys` names are expanded by trying configured sysname substitutions without installing a persistent `@sys` dentry.

Dentry validation:
- RCU validation checks parent deletion and callback validity, then compares `d_fsdata` against directory data version and `invalid_before`.
- Non-RCU validation may request a key, validate the parent directory, re-search for the name, and compare vnode/unique IDs.
- Positive dentries are invalidated if their target vnode changes or the unique generation changes.
- Negative dentries remain valid if the name is still absent.
- Deleted or pseudo-dir dentries are requested to be unhashed on final dput.

Mutation operations:
- Create, mkdir, symlink, link, unlink, rmdir, and rename allocate `afs_operation`, set vnode parameters and expected data-version deltas, dispatch AFS/YFS RPCs, commit returned statuses, update dentry versions, and patch directory caches if safe.
- New regular files, directories, and symlinks instantiate local inodes after successful server creation; new dirs and symlinks initialize local cached contents.
- Unlink validates the victim, uses sillyrename when the dentry is busy, and handles directory conflict by fetching victim status after the unlink.
- Rmdir locks the victim directory’s `rmdir_lock`, clears local deleted state on success, and normalizes `-EEXIST` to `-ENOTEMPTY`.
- Rename supports normal replacement, YFS no-replace, and YFS exchange. It drops dentries temporarily to avoid races with revalidation, handles busy replacement targets through sillyrename, adjusts subdirectory `..` data versions, patches local cached directories, and calls `d_move()` or `d_exchange()`.

Cache/writeback:
- Directory fscache cookies are used around read and mutation operations.
- `afs_dir_writepages()` writes valid directory folio-queue contents as a single blob to the cache while holding `validate_lock`; nonblocking writeback re-dirties the inode on lock conflict.
