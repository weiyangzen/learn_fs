# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fileext.h

Read completely: 74 lines.

This private header defines `struct __sfileext`, the extension storage attached to each `FILE`. It contains ungetc storage, wide-character I/O state, reusable `fgetstr` buffer state, and, in reentrant builds, mutex/condition/owner/count/cancellation fields for stream locking.

Important interactions: `_EXT`, `_UB`, lock macros, and `_FILEEXT_SETUP` are used throughout stdio allocation, locking, ungetc, and wide I/O.

Security/reliability notes: correct initialization through `_FILEEXT_SETUP` is required before stream locks or extension buffers are used.
