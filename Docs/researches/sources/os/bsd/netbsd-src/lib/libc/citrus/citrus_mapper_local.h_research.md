# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper_local.h

Internal ABI definition for Citrus mapper modules.

Key contents:
- Getops naming/declaration macros and ops-table macro.
- Function pointer typedefs for init, uninit, convert, and state init.
- ABI version `0x00000001`.
- `_citrus_mapper_ops` with method pointers.
- `_citrus_mapper_traits` with state size and M:N source/destination suspension limits.
- `_citrus_mapper` runtime object with ops, closure, module handle, traits, cache link, refcount, and key.

This file defines the binary/plugin boundary for mapper modules.
