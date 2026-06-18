# File Research: sources/os/bsd/netbsd-src/lib/libc/include/tsd.h

Private libc thread-specific data storage definition.

Defines:
- `TSD_KEYS_MAX 64`.
- `struct __libc_tsd` with value pointer, destructor, and in-use flag.
- External array `__libc_tsd[TSD_KEYS_MAX]`.

Used by libc thread-stub/TSD machinery.
