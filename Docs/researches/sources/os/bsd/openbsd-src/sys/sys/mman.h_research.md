# File Research: sources/os/bsd/openbsd-src/sys/sys/mman.h

Defines memory mapping, protection, advice, inheritance, sync, and locking constants plus userland prototypes.

Key contents:
- Protections: `PROT_NONE`, `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`.
- Mapping flags: `MAP_SHARED`, `MAP_PRIVATE`, `MAP_FIXED`, `MAP_ANON`, `MAP_STACK`, `MAP_CONCEAL`, internal `__MAP_NOREPLACE`, `__MAP_NOFAULT`.
- Legacy userland compatibility aliases such as `MAP_COPY` and `MAP_FILE`.
- Advice constants `POSIX_MADV_*` and BSD `MADV_*`.
- `MAP_INHERIT_*`, `MS_*`, and `MCL_*` constants.
- Userland prototypes for `mmap`, `mprotect`, `munmap`, `msync`, `mlock`, `munlock`, `madvise`, `minherit`, `mimmutable`, `mquery`, `shm_open`, and related calls.

Risk notes:
- `MAP_FLAGMASK` and internal flags must stay consistent with VM syscall validation.
