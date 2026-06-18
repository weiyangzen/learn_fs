# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat30.c

Read completely: 137 lines.

This implements `__stat30`, `__fstat30`, `__lstat30`, and `__fhstat40`. It calls the current `*50` stat APIs and converts native `struct stat` to `struct stat30`, using `timespec50` conversion for timestamps and preserving wider inode fields than `stat13`.

Important interactions: `__fhstat40` accepts an explicit file-handle size and delegates to `__fhstat50`.

Security/reliability notes: device fields still narrow to 32-bit compatibility layout. Timestamp handling follows the `time50` conversion helpers.
