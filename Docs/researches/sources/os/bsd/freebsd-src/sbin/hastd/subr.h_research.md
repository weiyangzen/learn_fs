# File Research: sources/os/bsd/freebsd-src/sbin/hastd/subr.h

`subr.h` declares shared HAST helper functions and the `KEEP_ERRNO(work)` macro, which preserves `errno` across cleanup code.

The exported functions cover append-formatting, provider information discovery, role-name formatting, and privilege dropping. The header includes `hast.h`, so the helper API is tied to `struct hast_resource`.
