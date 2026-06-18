# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lseek.h

Compatibility header for sparse-file seek support.

Behavior:
- Includes `<unistd.h>`.
- Defines `SEEK_DATA` as `3` if the platform C library does not define it.

Key role: allows code using `lseek(..., SEEK_DATA)` to compile against older libc headers.
