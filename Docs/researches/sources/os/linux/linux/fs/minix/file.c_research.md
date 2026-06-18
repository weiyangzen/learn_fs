# File Research: sources/os/linux/linux/fs/minix/file.c

## Purpose
`file.c` defines Minix regular-file operations, fsync behavior, and inode attribute updates for regular files.

## Main Responsibilities
- Implements `minix_fsync()` using `mmb_fsync()` over the Minix inode metadata buffer-head list.
- Defines `minix_file_operations` for generic llseek, read, write, mmap preparation, fsync, and splice-read.
- Implements `minix_setattr()` for VFS attribute changes, especially size changes.
- Defines `minix_file_inode_operations` with setattr and getattr.

## Control Flow
`minix_setattr()` validates the requested attribute change with `setattr_prepare()`. For size changes, it checks the new size, updates the VFS inode size with `truncate_setsize()`, and calls `minix_truncate()` to update Minix block mapping. It then copies remaining attributes with `setattr_copy()` and marks the inode dirty.

## Integration Points
- Uses generic VFS file helpers for most regular I/O behavior.
- Uses Minix inode private metadata buffer list for fsync.
- Uses `minix_truncate()` and `minix_getattr()` implemented elsewhere in the Minix driver.
- Uses `nop_mnt_idmap` for idmapped-mount-neutral ownership handling.

## Risks and Edge Cases
- Size changes are handled before generic attribute copy so block truncation follows the new VFS size.
- Minix relies on generic file read/write behavior; filesystem-specific behavior is concentrated in block mapping/truncation outside this file.
