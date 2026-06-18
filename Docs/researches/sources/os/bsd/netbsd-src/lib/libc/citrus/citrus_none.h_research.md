# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.h

Read completely: 36 lines.

This header declares the `NONE` module operation tables: `_citrus_NONE_ctype_ops`, `_citrus_NONE_stdenc_ops`, and `_citrus_NONE_stdenc_traits`.

It is consumed by the standard encoding loader for the built-in default encoding and by `citrus_none.c` users that need the static operation descriptors. It contains only declarations and an include guard.

Security/reliability notes: no direct runtime behavior.
