# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.h

Interface for Citrus dynamic module handling.

Key behavior:
- Defines opaque `_citrus_module_t`.
- Declares `_citrus_find_getops`, `_citrus_load_module`, and `_citrus_unload_module`.

Used by ctype, mapper, and iconv runtime loaders.
