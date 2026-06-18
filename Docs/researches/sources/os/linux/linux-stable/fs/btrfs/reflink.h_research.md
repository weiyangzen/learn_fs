# File Research: sources/os/linux/linux-stable/fs/btrfs/reflink.h

## Purpose

Declares the Btrfs file range remap entry point implemented in `reflink.c`.

## API

The header declares:

```c
loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in,
			      struct file *file_out, loff_t pos_out,
			      loff_t len, unsigned int remap_flags);
```

This is the Btrfs-specific clone/dedupe backend used by file operations.

## Structure

The header contains only include guards, `<linux/types.h>`, a forward declaration of `struct file`, and the function prototype. It keeps reflink implementation details private to `reflink.c`.
