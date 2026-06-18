# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.h

Macro wrapper around BSD `LIST` hash tables plus a string hash declaration.

Key behavior:
- Defines macros for entry fields, fixed-size hash-head structs, init, remove, insert, and linear bucket search.
- Declares `_citrus_string_hash_func`.

Used by Citrus mapper/iconv shared-object caches.
