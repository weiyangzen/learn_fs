# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/local.h

Read completely: 36 lines.

Internal stdlib header for environment handling. It includes basic types and declares `__envvarnamelen()`, `__freeenvvar()`, `__allocenvvar()`, and `__canoverwriteenvvar()`.

This is the small shared interface used by `_env.c` and public environment mutation/query implementations.
