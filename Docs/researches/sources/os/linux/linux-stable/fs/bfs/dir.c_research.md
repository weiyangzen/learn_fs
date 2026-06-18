# File Research: sources/os/linux/linux-stable/fs/bfs/dir.c

This file implements BFS directory file and inode operations: readdir, create, lookup, hard link, unlink, rename, adding entries, and finding entries.

Exports:
- `bfs_dir_operations`
- `bfs_dir_inops`

Important flows:
- `bfs_readdir()` validates `ctx->pos` alignment, reads directory blocks from `i_sblock`, emits nonzero directory entries, and advances by fixed `BFS_DIRENT_SIZE`.
- `bfs_fsync()` syncs metadata buffer tracking with `mmb_fsync()`.
- `bfs_create()` allocates a VFS inode, claims the first free inode bit under `bfs_lock`, initializes file operations and mapping ops, inserts into hash, marks dirty, and adds a directory entry.
- `bfs_lookup()` checks name length, searches directory entries under lock, and calls `bfs_iget()`.
- `bfs_link()` adds a directory entry, increments link count, updates ctime, and instantiates the new dentry.
- `bfs_unlink()` finds the directory entry, clears its inode number, marks metadata dirty, updates directory/inode times, and decrements link count.
- `bfs_rename()` supports only default rename and `RENAME_NOREPLACE`, rejects directories, adds/reuses the target entry, clears the old entry, updates timestamps/link counts, and marks old metadata dirty.
- `bfs_add_entry()` scans the existing directory block range for a free fixed-size entry.
- `bfs_find_entry()` scans fixed-size entries by name.

Integration:
- Uses `bfs_lock` to serialize directory mutation and lookup.
- Uses `mmb_mark_buffer_dirty()` so directory metadata buffers can participate in fsync.
- Uses fixed BFS directory-entry format from `<linux/bfs_fs.h>`.

Risk notes:
- Directories do not grow by allocating new blocks here; `bfs_add_entry()` returns `-ENOSPC` when existing directory blocks have no free entry.
- Rename does not mark the newly created target directory buffer dirty in the same visible way as old entry clearing when `bfs_add_entry()` succeeds internally; correctness relies on `bfs_add_entry()` doing its own dirty marking.
- Directory reads skip unreadable blocks by advancing to the next block instead of returning an error.
