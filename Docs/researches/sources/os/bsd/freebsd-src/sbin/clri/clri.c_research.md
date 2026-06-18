# File Research: sources/os/bsd/freebsd-src/sbin/clri/clri.c

## Purpose
Clears selected UFS inode records on a special device, preserving only an incremented generation number.

## Main Elements
- `usage()`: requires device plus one or more inode numbers.
- `main()`: opens UFS disk metadata with `ufs_disk_fillout()`, iterates inode arguments, validates inode number, reads inode with `getinode()`, zeros UFS1 or UFS2 dinode body, increments `di_gen`, writes with `putinode()`, and calls `fsync()`.

## Dependencies And Integration
Uses `<libufs.h>` and UFS/FFS dinode definitions. Intended as a low-level administrative repair tool.

## Risk Notes
This is destructive by design. Inode parsing uses `atoi()`, so malformed numeric strings can collapse to invalid low numbers but are not fully diagnosed.
