# File Research: sources/local-fs/kdave-linux/fs/btrfs/reflink.h

## Purpose

`reflink.h` declares the Btrfs file range remap entry point implemented by `reflink.c`.

## Interface

It forward-declares `struct file` and exposes:

`loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`

This function is the filesystem implementation for clone/dedupe remap operations.

## Build Role

The header is minimal: it provides include guards, includes `linux/types.h`, and lets other Btrfs file operation code call the remap implementation without pulling in the full implementation details.
