# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmemcpywrap.c

Adapter that gives `kmemcpy()` a generic copy-function shape.

Key behavior:
- `kmemcpywrap(from, to, size)` calls `kmemcpy(to, (u_long)from, size)`.
- Used by printers that accept a `copyfunc_t` for either kernel-memory or local-memory traversal.

Research notes:
- Treats `from` as a kernel virtual address, not a normal source pointer.
