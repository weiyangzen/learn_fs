# File Research: sources/teaching/os161/kern/include/kern/seek.h

Defines shared `lseek` origin constants.

Constants:
- `SEEK_SET`
- `SEEK_CUR`
- `SEEK_END`

Relevance:
- VFS/filehandle layers use these to interpret seek requests; semfs semaphore files report non-seekable while SFS files/directories are seekable.
