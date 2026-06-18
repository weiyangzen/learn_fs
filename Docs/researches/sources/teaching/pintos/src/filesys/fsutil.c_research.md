# File Research: sources/teaching/pintos/src/filesys/fsutil.c

## Purpose
Implements Pintos file-system utility commands used by kernel command-line actions: listing, dumping, deleting, extracting from scratch disk, and appending to a scratch-disk ustar archive.

## Key Functions
- `fsutil_ls(argv)`
  - Opens the root directory and prints live entries.
- `fsutil_cat(argv)`
  - Opens a file and hex-dumps its contents to the console one page at a time.
- `fsutil_rm(argv)`
  - Removes a named file.
- `fsutil_extract(argv)`
  - Reads a ustar archive from `BLOCK_SCRATCH`.
  - Ignores directory entries.
  - Creates Pintos files for regular archive entries.
  - Copies file data sector by sector.
  - Zeros the first two scratch sectors afterward to mark archive EOF.
- `fsutil_append(argv)`
  - Opens a Pintos file.
  - Appends it as a ustar regular file to `BLOCK_SCRATCH`.
  - Maintains a static scratch-sector append position.
  - Writes two zero sectors as the ustar end marker without advancing past them.

## Important Behavior
- `fsutil_extract()` and `fsutil_append()` each use a static `block_sector_t sector`, independent from one another.
- `extract` should precede `append`, per the file comment, because their scratch positions are independent.
- Archive directories are not recreated in the Pintos file system.
- `fsutil_append()` overwrites the previous EOF marker on subsequent appends because it does not advance past the two zero EOF sectors.
- `fsutil_append()` checks space while writing file data, but not explicitly before writing the two EOF marker sectors.
- The code uses Pintos panic-on-error style for utility failures.

## Dependencies
- `filesys/directory.h` for root listing.
- `filesys/file.h` and `filesys/filesys.h` for file operations.
- `ustar.h` for archive parse/write helpers.
- `threads/palloc.h` and `threads/vaddr.h` for page-sized cat buffer.
- Block role `BLOCK_SCRATCH` for host-transfer archive staging.

## Research Notes
- This file is operational glue for the teaching OS test harness, not a general-purpose user command implementation.
- `buffer + chunk_size` in `fsutil_append()` relies on compiler support for pointer arithmetic on `void *`, which is accepted by GCC-style toolchains used by Pintos.
