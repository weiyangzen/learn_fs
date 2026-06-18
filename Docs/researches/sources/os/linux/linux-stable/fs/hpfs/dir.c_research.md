# File Research: sources/os/linux/linux-stable/fs/hpfs/dir.c

## Purpose

Implements HPFS directory VFS operations: lseek, readdir, lookup, release, and directory file operations.

## Main Entry Points

- `hpfs_readdir()`
- `hpfs_lookup()`
- `hpfs_dir_lseek()`
- `hpfs_dir_ops`

## Control Flow And State

Directory positions encode dnode sector and dirent index. `hpfs_readdir()` emits `.` and `..`, registers the file position for later dnode mutation fixups, walks dirents through `map_pos_dirent()`, skips sentinel first/last entries, translates names for lowercase mount behavior, and emits entries.

Lookup validates and adjusts the target name, searches the dnode tree, instantiates the fnode inode with `iget_locked()`, optionally reads the fnode when directory or EA metadata is needed, and fills inode size/time/mode information from the directory entry when possible.

## Dependencies

Uses dnode tree traversal, inode initialization, code-page name translation, and HPFS global locking.

## Risks

Directory position tracking is tied to mutation code in `dnode.c`; missed `hpfs_del_pos()` calls can leave stale position pointers. Lookup rejects HPFS386 ACL/XPERM entries for writable mounts because this driver does not support those structures.
