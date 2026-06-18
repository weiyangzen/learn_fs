# File Research: sources/local-fs/e2fsprogs/misc/mklost+found.c

`mklost+found.c` implements the standalone `mklost+found` utility for mounted ext filesystems.

Core behavior:
- Requires no arguments.
- Creates a `lost+found` directory with mode `0700`.
- Repeatedly creates long temporary files inside it until the directory size exceeds `(EXT2_NDIR_BLOCKS - 1) * st_blksize`.
- Deletes all temporary files after expansion.
- Exits nonzero on mkdir/create/stat/unlink errors.

Implementation details:
- Temporary names are 246 `x` characters plus an 8-digit number, staying within ext directory name limits.
- Uses normal POSIX filesystem operations (`mkdir`, `creat`, `stat`, `unlink`) rather than libext2fs.
- Prints version banner from `../version.h`.
- Uses NLS support for translated usage text.

Research notes:
- The file relies on the mounted filesystem allocating directory blocks as a side effect of creating many entries.
- It is intentionally simple and assumes it is run in the target filesystem directory where `lost+found` should be created.
