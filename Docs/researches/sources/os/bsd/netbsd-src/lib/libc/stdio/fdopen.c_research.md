# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fdopen.c

Read completely: 123 lines.

This file implements `fdopen`. It parses mode flags, verifies the descriptor fits in the `FILE` short `_file` field, checks that requested access is compatible with `fcntl(F_GETFL)`, optionally enforces regular-file mode, allocates a `FILE`, and installs standard read/write/seek/close hooks.

Important interactions: uses `__sflags`, `__sfp`, `__sread`, `__swrite`, `__sseek`, and `__sclose`.

Security/reliability notes: handles append mode specially when the underlying descriptor lacks `O_APPEND`, and fails descriptors at or above `USHRT_MAX`.
