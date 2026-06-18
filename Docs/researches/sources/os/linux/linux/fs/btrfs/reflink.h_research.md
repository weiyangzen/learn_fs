# File Research: sources/os/linux/linux/fs/btrfs/reflink.h

## Scope

`reflink.h` declares the Btrfs remap/reflink entry point.

## API

- `btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags)`

This function is implemented in `reflink.c` and is used as the filesystem-specific clone/dedupe remap handler.

## Dependencies And Invariants

The header forward-declares `struct file` and includes Linux basic types. Callers must pass VFS file objects and remap flags accepted by the implementation.
