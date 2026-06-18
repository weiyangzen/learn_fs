# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.h

Declares legacy DOS disk I/O structures, constants, error globals, and helper macros for the DOS libext2fs I/O manager.

Key structures:
- `CHS`: cylinder/head/sector plus byte offset.
- `PARTITION`: Linux-style device name, BIOS drive number, LBA start, sector length, partition number, and geometry.
- `PTABLE_ENTRY`: packed PC partition table entry.

Constants:
- BIOS operation codes: read, write, get geometry, ready.
- Module error codes: bad device, hardware, unsupported, not ext2fs, empty partition, Linux swap.
- Hardware status macros such as `HW_OK`, `HW_WRITE_PROT`, `HW_NO_SECTOR`, and others.

Exports:
- `_dio_error`
- `_dio_hw_error`
- `open_partition(char *dev)`

Implementation notes:
- The header requires Turbo C large memory model when `__TURBOC__` is defined.
- The documented `open_partition` behavior claims extended partition traversal, but `dosio.c` does not implement it.
- `open_partition` is declared here but not implemented in the paired `dosio.c` shown in this group.
