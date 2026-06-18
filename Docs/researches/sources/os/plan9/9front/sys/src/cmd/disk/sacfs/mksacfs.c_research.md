# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/mksacfs.c

## Purpose
Builds a SAC filesystem image from a directory tree or single file.

## Key Behavior
- Accepts `-o output`, optional `-b blocksize`, and `-u` to force uncompressed blocks.
- Writes a `SacHeader` followed by a root `SacDir`, then recursively emits file/directory block tables and data blocks.
- Stores all multi-byte metadata using big-endian `putl()` fields defined by the SAC format headers.
- For regular files, writes an offset table of block starts plus a final end offset, compressing each block with `sac()` when it saves space.
- Marks compressed blocks by storing the block offset as a negative value in the offset table.
- For directories, recursively builds child `SacDir` records, packs them into blocks, optionally compresses each directory block, and stores directory length as entry count.
- `setsd()` copies names/owners/groups, assigns monotonically increasing qid values with directory mode bits, and records mode/time/length/block-table offset.

## Interfaces And Dependencies
- Uses `sac.h` for `sac()` and `sacfs.h` for `SacHeader`/`SacDir` layouts.
- Uses Plan 9 `Dir`, `dirreadall`, and normal filesystem reads.

## Notes
The `seen()` cache is implemented but not used in traversal, so hard-link/cycle suppression is not active. The program currently requires `-o`; the temp-file path is left as a fatal “still to do” branch.
