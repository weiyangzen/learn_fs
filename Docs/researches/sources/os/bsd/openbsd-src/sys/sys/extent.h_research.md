# File Research: sources/os/bsd/openbsd-src/sys/sys/extent.h

This header defines the extent allocator interface used for address/resource range management.

Key definitions:
- `struct extent_region` with start/end/flags and list linkage.
- Region flags: `ER_ALLOC`, `ER_DISCARD`.
- `struct extent` with name, allocated regions, range, memory type, flags, and global linkage.
- `struct extent_fixed` for preallocated descriptor storage.
- Internal extent flags: `EXF_FIXED`, `EXF_NOCOALESCE`, `EXF_WANTED`, `EXF_FLWANTED`.
- Allocation flags: `EX_NOWAIT`, `EX_WAITOK`, `EX_FAST`, `EX_CATCH`, `EX_NOCOALESCE`, `EX_MALLOCOK`, `EX_WAITSPACE`, `EX_BOUNDZERO`, `EX_CONFLICTOK`, `EX_FILLED`.
- Placeholders: `EX_NOALIGN`, `EX_NOBOUNDARY`.

Kernel/testing APIs:
- `EXTENT_FIXED_STORAGE_SIZE`
- `extent_create`, `extent_destroy`
- `extent_alloc_subregion`, `extent_alloc_subregion_with_descr`
- `extent_alloc_region`, `extent_alloc_region_with_descr`
- `extent_free`, `extent_print`, `extent_print_all`
- Convenience macros `extent_alloc` and `extent_alloc_with_descr`.

Risk notes:
- Extents can sleep, allocate memory, or use fixed storage depending on flags; callers must choose flags appropriate to context.
- Boundary/alignment semantics are encoded in allocation API parameters, not the extent object alone.
