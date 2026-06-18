# File Research: sources/os/bsd/dragonflybsd/sys/sys/fcntl.h

`fcntl.h` defines open flags, file-status flags, descriptor flags, record locking structures, `fcntl()` command numbers, `at`-family constants, permission bits, advisory locking constants, and userland function declarations.

It distinguishes user open flags from kernel `f_flag` encoding, with kernel conversion macros `FFLAGS()` and `OFLAGS()`. DragonFly-specific or BSD-visible flags include forced blocking/nonblocking/append/offset/sync/async write flags, `O_DIRECT`, close-on-fork support, `F_GETPATH`, `F_MAXFD`, and dup variants with close-on-exec or close-on-fork.

The header declares `struct flock`, kernel `union fcntl_dat`, `open()`, `openat()`, `creat()`, `fcntl()`, `flock()`, `posix_fadvise()`, and `posix_fallocate()` under the appropriate visibility gates.
