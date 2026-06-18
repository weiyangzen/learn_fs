# File Research: sources/os/linux/linux/io_uring/fs.h

## Purpose
Declares io_uring filesystem namespace opcode handlers and cleanup functions.

## Main Contents
- Prototypes for rename, unlink, mkdir, symlink, and link prep/issue functions.
- Cleanup prototypes for rename, unlink, mkdir, and link path resources.

## Cross-File Relationships
- Implemented by `fs.c`.
- Used by io_uring opcode dispatch and cleanup paths.

## Risks / Review Notes
- Cleanup declarations mirror operations that allocate delayed filenames; any new pathname opcode should follow the same pattern.
