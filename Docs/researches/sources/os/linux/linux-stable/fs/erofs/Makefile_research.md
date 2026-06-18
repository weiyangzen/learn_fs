# File Research: sources/os/linux/linux-stable/fs/erofs/Makefile

## Summary
Builds EROFS core and optional feature objects.

## Main Contents
Core objects:
- `super.o`
- `inode.o`
- `data.o`
- `namei.o`
- `dir.o`
- `sysfs.o`

Optional objects cover xattrs, compressed data, decompressor algorithms, crypto acceleration, file-backed I/O, fscache, and page-cache sharing.

## Risks
The object list mirrors the feature matrix; missing config options directly remove decompressor or backend support.
