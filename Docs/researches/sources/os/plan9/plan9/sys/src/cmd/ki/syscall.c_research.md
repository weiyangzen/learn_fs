# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/syscall.c

This file emulates Plan 9 syscalls for SPARC programs running under `ki` by translating arguments from emulated memory/registers into host Plan 9 libc calls.

It includes Plan 9 syscall numbers, maps them to names in `sysctab[]`, and dispatches through `systab[]` from `ta()`, using `reg.r[REGRET]` as the syscall number and return register.

Implemented calls include errstr variants, fd2path, bind, chdir, close, dup, exits, open, read/pread, seek/old seek, rfork without process creation, sleep, old/new stat and fstat, write/pwrite, pipe, create, brk, remove, notify, and segflush. Unsupported syscalls print a diagnostic and exit.

The file uses `memio()`, `getmem_w()`, and `putmem_w()` to copy strings, buffers, stat data, pipe fds, and 64-bit offsets between host and emulated memory. It maintains `errbuf` and handles Bss growth in `sysbrk_()` by resizing the Bss segment table.

Filesystem relevance is substantial: this is the emulator’s bridge for Plan 9 file namespace, fd, stat, read/write, create/remove, bind, and path operations.
