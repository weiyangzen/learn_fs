# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.c

## Purpose
Implements core file and directory entry operations: lookup by name, inode creation, unlink/deallocation, directory-entry append, and directory-entry removal.

## Main Interfaces
- `v7fs_file_lookup_by_name()` scans a parent directory with `v7fs_datablock_foreach()`.
- `v7fs_file_allocate()` allocates an inode, initializes attributes/type-specific state, creates `.` and `..` for directories, writes the inode, and links it into the parent directory.
- `v7fs_file_deallocate()` removes a name, decrements/removes inode links, enforces empty-directory rules, and shrinks directory data.
- `v7fs_directory_add_entry()` expands a directory and writes the new fixed-size dirent at the end.
- `v7fs_directory_remove_entry()` replaces the removed entry with the last dirent, then contracts the directory.

## Implementation Notes
Directory deletion requires exactly `.` and `..` to remain. Special device files store the device number in `inode.device` and `addr[0]`. Directory entry mutation uses disk-endian inode values where appropriate.

## Dependencies
Uses inode allocation/load/writeback, datablock expansion/contraction, dirent normalization/conversion, scratch buffers, and the mount I/O callbacks.
