# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdents.c

Read completely: 92 lines.

This implements libc12-compatible `getdents`. It calls `__getdents30` to fill the user buffer with current `dirent` records, then converts them in place to smaller `dirent12` records, narrowing inode numbers to 32-bit and truncating names to the old fixed name buffer if needed.

Important interactions: in-place conversion relies on `dirent12` being smaller than current `dirent`.

Security/reliability notes: the code avoids unaligned 64-bit inode access with `memcpy`. Inode and long-name truncation are compatibility behavior.
