# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/ealloc.c

Fatal-on-failure allocation wrappers used by rcorder.

Key elements:
- `enomem` exits with `errx(2, "Cannot allocate memory.")`.
- `emalloc`, `estrdup`, `erealloc`, and `ecalloc` wrap standard allocation functions and abort on failure.

Dependencies:
- Declared by `ealloc.h`.
- Used by `hash.c` and `rcorder.c`.

Research notes:
- These helpers simplify rcorder graph code by making allocation failure nonrecoverable and avoiding repeated null checks.
