# File Research: sources/os/linux/linux/fs/bfs/dir.c

## Purpose
Implements BFS directory reading and directory inode operations: create, lookup, link, unlink, rename, and directory entry helpers.

## Directory Iteration
- `bfs_readdir()`:
  - validates directory position alignment to `BFS_DIRENT_SIZE`
  - reads directory blocks using contiguous block range from `BFS_I(dir)`
  - emits nonzero `ino` entries
  - advances `ctx->pos` by fixed directory-entry size

## Directory File Operations
- `read = generic_read_dir`
- `iterate_shared = bfs_readdir`
- `fsync = bfs_fsync`
- `llseek = generic_file_llseek`

`bfs_fsync()` syncs metadata buffer heads via `mmb_fsync()`.

## Inode Operations
- `bfs_create()`:
  - allocates new VFS inode
  - finds free inode bit under global BFS mutex
  - initializes regular-file inode ops and mapping ops
  - marks inode dirty
  - adds directory entry
- `bfs_lookup()`:
  - rejects names longer than `BFS_NAMELEN`
  - finds matching directory entry under mutex
  - loads target with `bfs_iget()`
- `bfs_link()`:
  - adds another directory entry, increments link count, updates ctime, and instantiates dentry
- `bfs_unlink()`:
  - finds matching entry, clears `de->ino`, marks metadata dirty, updates timestamps, decrements link count
- `bfs_rename()`:
  - supports only `RENAME_NOREPLACE`
  - rejects directory renames
  - finds old and optional new entries
  - adds new entry if needed, clears old entry, decrements overwritten inode link count

## Directory Entry Helpers
- `bfs_add_entry()` scans existing directory blocks for a free fixed-size slot, extends directory size only within preallocated directory blocks, fills fixed-length name field, and marks metadata dirty.
- `bfs_namecmp()` handles fixed-length BFS names and NUL termination.
- `bfs_find_entry()` scans directory contents by block and offset.

## Research Notes
BFS directories are fixed-record arrays in contiguous blocks. There is no directory block growth path here beyond consuming existing free slots, so `bfs_add_entry()` can return `-ENOSPC` even if free disk blocks exist.
