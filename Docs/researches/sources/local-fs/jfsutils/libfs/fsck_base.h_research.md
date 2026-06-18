# File Research: sources/local-fs/jfsutils/libfs/fsck_base.h

## Purpose
Provides fsck-wide base macros for inode mode classification and shared page/bit/byte sizing constants.

## Key Definitions
- File type predicates: `ISDIR`, `ISREG`, `ISLNK`, `ISBLK`, `ISCHR`, `ISFIFO`, `ISSOCK`, masking with `IFMT`.
- Fixed page geometry: `BYTESPERPAGE` 4096, `BITSPERPAGE`, `BITSPERDWORD`, `BITSPERBYTE`, and log2 equivalents.
- Workspace allocation unit: `MEMSEGSIZE` is 64 KiB.
- `log2BYTESPERKBYTE` is 10.

## Dependencies
Assumes `IFMT`, `IFDIR`, `IFREG`, and related inode mode constants are already visible from JFS headers included by consumers.

## Notes
The constants are foundational for fsck workspace sizing in `fsckwsp.h` and buffer sizes throughout the fsck/logredo code.
