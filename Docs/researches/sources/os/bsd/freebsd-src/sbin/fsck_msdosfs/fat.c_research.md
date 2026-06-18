# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/fat.c

## Purpose

Loads, validates, repairs, writes, and scans FAT12/FAT16/FAT32 allocation tables. It also tracks chain heads to identify lost cluster chains.

## Core Data Structures

- `struct fat_descriptor`: private FAT state containing boot pointer, FAT buffer, accessor callbacks, head bitmap, file descriptor, mmap/cache state, and FAT32 cache state.
- `long_bitmap_t`: bitmap where set bits represent possible chain heads.
- `struct fat32_cache_entry`: LRU cache entry for large FAT32 tables when mmap is unavailable.

## Main Entry Points

- `readfat(int fs, struct bootblock *boot, struct fat_descriptor **fp)`
- `writefat(struct fat_descriptor *fat)`
- `checkdirty(int fs, struct bootblock *boot)`
- `cleardirty(struct fat_descriptor *fat)`
- `checkchain(struct fat_descriptor *fat, cl_t head, size_t *chainsize)`
- `checklost(struct fat_descriptor *fat)`
- `clearchain(struct fat_descriptor *fat, cl_t head)`
- Accessors: `fat_get_cl_next()`, `fat_set_cl_next()`, `fat_is_valid_cl()`, `fat_is_cl_head()`, `fat_clear_cl_head()`

## FAT Access

Implements separate get/set callbacks for:
- FAT12 packed 12-bit entries
- FAT16 little-endian 16-bit entries
- FAT32 little-endian 28-bit entries
- FAT32 cached access for large non-mmap tables

## Head Bitmap Algorithm

`readfat()` initializes every cluster as a possible chain head, then scans the FAT:
- Free and bad clusters are cleared from the head map.
- Valid next-cluster pointers clear the pointed-to cluster as a head.
- Cross-linked chains are detected when a next cluster was already cleared.
- Remaining head bits after directory traversal are candidates for lost chains.

## Repair Logic

- Odd FAT signatures can be corrected.
- Dirty FAT16/FAT32 signatures are detected.
- Out-of-range chain links can be truncated to EOF.
- Cross-linked chains can be truncated.
- `checkchain()` validates a claimed chain and can truncate or clear invalid endings.
- `checklost()` reconnects remaining chains through `reconnect()` or clears them, then fixes FAT32 FSInfo hints.

## I/O Strategy

Attempts `mmap()` unless disabled. For large FAT32 without mmap, keeps a 4 MiB working buffer split into 128 KiB LRU chunks and flushes dirty cache entries before copying FAT0 to backup FATs.

## Risk Notes

The bitmap is both an ownership model and lost-chain detector. Any missed `fat_clear_cl_head()` can create false lost chains; any premature clearing can hide real lost data. Cached FAT32 mode must flush dirty chunks before backup FAT copies.
