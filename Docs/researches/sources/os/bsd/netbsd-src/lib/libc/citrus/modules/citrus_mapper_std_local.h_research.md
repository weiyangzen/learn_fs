# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_local.h

Read completely: 70 lines.

This header defines private in-memory structures for mapper_std. It includes linear zones, rowcol mapper state, converter/uninit function pointer types, and the top-level `_citrus_mapper_std` object containing the mapped file region, DB handle, dispatch callbacks, and type-specific union.

Important interactions: consumed only by `citrus_mapper_std.c` through `citrus_mapper_std.h`.

Security/reliability notes: no executable code. The design keeps file-backed table data in `_citrus_region` and heap-allocated parsed row/column zone metadata in `rc_src_rowcol`.
