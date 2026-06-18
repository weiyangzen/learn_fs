# File Research: sources/os/bsd/openbsd-src/sys/kern/Makefile

Kernel support Makefile for generated syscall files and tags.

Key behavior:
- `all` intentionally does nothing and suggests `make syscalls`.
- `syscalls` target regenerates `init_sysent.c`.
- `init_sysent.c`, `syscalls.c`, `../sys/syscall.h`, and `../sys/syscallargs.h` depend on `makesyscalls.sh` and `syscalls.master`.
- Defines architecture list for tags generation.
- Builds per-architecture tags and creates symlinks through `/var/db/sys_tags`.
- `DGEN` lists generic kernel/source directories receiving tag links, including VFS and filesystem directories such as `kern`, `ufs`, `msdosfs`, `nfs`, and `miscfs`.

Filesystem/OS relevance:
- Maintains syscall table generation and kernel source navigation metadata.
