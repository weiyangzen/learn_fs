# File Research: sources/os/linux/linux-stable/fs/hfsplus/wrapper.c

## Purpose

Handles low-level HFS+ volume-header discovery and block I/O, including HFS wrapper support and multisession CD-ROM offsets. It prepares superblock fields needed by the rest of HFS+ mounting.

## Main Entry Points

- `hfsplus_submit_bio()`: aligns HFS+ sector-based I/O to the device logical block size and calls `bdev_rw_virt()`.
- `hfsplus_read_wrapper()`: finds the real HFS+ volume header, handles HFS wrapper and partition-map indirection, reads primary/backup volume headers, and initializes block-size/offset fields.
- `hfsplus_get_last_session()`: selects explicit or last CD-ROM session start.
- `hfsplus_read_mdb()`: validates an HFS wrapper MDB and extracts embedded HFS+ extents.

## Control Flow And State

`hfsplus_read_wrapper()` allocates primary and backup volume-header buffers, reads sector 2 relative to the current partition/session, and loops when it encounters an HFS wrapper or partition map. Once an HFS+/HFSX signature is found, it validates the backup header, derives allocation block size, chooses a VFS block size aligned to the partition offset, and stores `blockoffset`, `part_start`, `sect_count`, and `fs_shift` in `hfsplus_sb_info`.

## Dependencies

Depends on Linux block-device helpers, CD-ROM TOC/multisession APIs, HFS+ raw offsets/signatures, `hfs_part_find()`, and `hfsplus_min_io_size()`.

## Risks

Mount correctness depends on precise sector arithmetic and alignment. Failure cleanup frees allocated header buffers, but callers must treat failure as mount abort. HFS wrapper and partition-map loops trust validation helpers to avoid accepting inconsistent embedded offsets.
