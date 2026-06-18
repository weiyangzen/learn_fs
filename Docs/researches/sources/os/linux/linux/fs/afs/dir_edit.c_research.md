# File Research: sources/os/linux/linux/fs/afs/dir_edit.c

Purpose: edits the client’s cached AFS directory blob after successful server-side create, mkdir, symlink, link, unlink, rmdir, rename, sillyrename, or subdirectory parent changes.

Key interfaces:
- `afs_edit_dir_add()`.
- `afs_edit_dir_remove()`.
- `afs_edit_dir_update()`.
- `afs_mkdir_init_dir()`.

Implementation notes:
- Directory blocks contain 64 fixed slots with an 8-byte bitmap; names may consume multiple contiguous 32-byte dirent slots.
- `afs_find_contig_bits()`, set, and clear helpers manage contiguous slot allocation in the block bitmap.
- `afs_dir_get_block()` maps a requested directory block from the vnode’s folio queue, extending storage with `netfs_alloc_folioq_buffer()` when adding blocks.
- New blocks are initialized with AFS directory magic, reserved metadata bitmap entries, and allocation counters in block 0.
- Add chooses a block with sufficient free slots, initializes a new block if necessary, writes vnode/unique/name, adjusts bitmap/allocation counter, links into the hash bucket, increments inode version, and marks the inode dirty.
- Remove locates the entry through the hash-chain search helper, clears bitmap and dirent slots, adjusts allocation counters, repairs hash-chain predecessor or bucket head, sets inode version to server data version, and marks dirty.
- Update scans blocks linearly for an entry and rewrites the vnode/unique pair, used especially for `..` updates.
- New mkdir cache initialization creates block 0 plus `.` and `..`, adjusts counters, marks directory valid/read, and marks dirty.

Dependencies:
- Folio queue directory storage, directory search helper functions, netfs dirty marking, AFS directory constants and XDR structs.

Edge cases:
- If directory size is invalid, too large, not block-aligned, callback-broken, or hash-chain expectations fail, the directory cache is invalidated for redownload.
- `afs_edit_dir_add()` notes a TODO around maintaining `hash_next`, but it does update the bucket head and new entry link.
