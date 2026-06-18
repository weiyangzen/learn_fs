# File Research: sources/os/linux/linux-stable/fs/hpfs/alloc.c

## Purpose

Implements HPFS allocation bitmap management, dnode/fnode/anode allocation, free counters, and discard trimming.

## Main Entry Points

- `hpfs_alloc_sector()`, `hpfs_alloc_if_possible()`, `hpfs_free_sectors()`
- `hpfs_check_free_dnodes()`, `hpfs_alloc_dnode()`, `hpfs_free_dnode()`
- `hpfs_alloc_fnode()`, `hpfs_alloc_anode()`
- `hpfs_chk_sectors()`
- `hpfs_trim_fs()`

## Control Flow And State

Main bitmap bits use `1` for free and `0` for allocated. Allocation searches near a target sector, cached bitmap, then all bitmaps, reducing forward preallocation demand if needed. Directory dnodes prefer or avoid the directory band depending on free dnode pressure. Free counters are maintained unless an underflow/overflow is detected, in which case the count is invalidated with `(unsigned)-1`.

`hpfs_alloc_dnode()` initializes a 2048-byte dnode across four sectors with magic, first-free offset, sentinel dirents, and self pointer. Fnodes and anodes are initialized with their magic values and B+ tree free-node counts. `hpfs_trim_fs()` scans free runs in the directory-band bitmap and main bitmaps and issues discard requests within caller-supplied bounds.

## Dependencies

Uses bitmap mapping from `map.c`, four-sector buffer helpers from `buffer.c`, and HPFS superblock state.

## Risks

Allocation correctness depends on bitmap bit semantics and 4-sector dnode alignment. Dnode splitting callers rely on `hpfs_check_free_dnodes()` to avoid mid-operation ENOSPC corruption. Trim takes the HPFS global lock per bitmap and returns `-EROFS` if the filesystem becomes read-only.
