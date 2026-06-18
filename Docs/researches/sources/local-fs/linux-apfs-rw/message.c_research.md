# File Research: sources/local-fs/linux-apfs-rw/message.c

## Purpose
Provides the module’s centralized APFS logging helper.

## Main Function
- `apfs_msg()`: formats APFS log messages with kernel log prefix, superblock ID or `?`, optional function and line metadata, and a varargs message.

## Dependencies
Uses Linux `fs.h`, `printk()`, `va_format`, and APFS logging macros declared in `apfs.h`.

## Notes
The helper supports callers without a superblock by printing `APFS (?)`.
