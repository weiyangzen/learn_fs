# File Research: sources/teaching/minix/minix/fs/procfs/const.h

`const.h` defines ProcFS sizing and mode constants. `NR_INODES` is set to four times the combined task/process count, with a detailed comment explaining the need for static files, retained deleted inodes still open in VFS, and stable getdents generation for PID directories.

The file defines standard modes for world-readable regular files (`REG_ALL_MODE`), world-accessible directories (`DIR_ALL_MODE`), and symlinks (`LNK_ALL_MODE`). `BUF_SIZE` is `4097`, allowing a 4KB user-visible output buffer plus one byte needed by `vsnprintf` handling in `buf.c`.
