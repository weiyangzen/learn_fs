# File Research: sources/os/linux/linux-stable/fs/minix/file.c

## Summary
Regular file operations and inode attribute updates for Minix.

## Main APIs
`minix_fsync()`, `minix_file_operations`, `minix_setattr()`, and `minix_file_inode_operations`.

## Behavior
Regular files use generic llseek/read/write/mmap/splice helpers. `minix_fsync()` delegates to `mmb_fsync()` with the inode’s metadata buffer-head list. `minix_setattr()` validates attributes, handles size changes by checking the new size, updating `i_size`, and calling `minix_truncate()`, then copies remaining attributes and marks the inode dirty.

## Dependencies
Generic VFS file helpers, buffer-head metadata syncing, Minix inode private metadata buffers, `minix_truncate()`, and `minix_getattr()`.

## Risks
Size updates are non-journaled and depend on truncate plus dirty inode writeback. The idmap argument is ignored in favor of `nop_mnt_idmap`, matching this filesystem’s legacy behavior.
