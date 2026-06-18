# File Research: sources/os/bsd/netbsd-src/sys/sys/vmem.h

Read completely: 102 lines.

Public interface for NetBSD's `vmem(9)` resource allocator. It declares the opaque `vmem_t` arena type, address/size/flag typedefs, global kernel arenas, import/release callback types, allocation/free routines, diagnostics, and sizing helpers.

Core API:
- Arena creation supports fixed-size import (`vmem_create`) and extended import (`vmem_xcreate`) callbacks, plus parent arenas and quantum/import-size parameters.
- Allocation APIs include normal allocation/free, constrained allocation (`vmem_xalloc`), fixed-address allocation (`vmem_xalloc_addr`), constrained free, free-all, and adding spans.
- Diagnostics include rehash start, `vmem_whatis`, `vmem_print`, and `vmem_printall`.
- Flags distinguish sleep behavior, instant/best fit, bootstrap/populating modes, large/extended import, and private tags.

Integration notes:
- Exposes `kmem_arena`, `kmem_meta_arena`, and `kmem_va_arena` for kernel allocation layers.
- Usable outside `_KERNEL` with `<stdbool.h>` for standalone/test builds.

Risks and notes:
- Callers must pass matching address/size pairs back to the correct arena; the API is low-level and trusts the caller.
- `VM_SLEEP` versus `VM_NOSLEEP` controls blocking behavior and is important in interrupt or lock-sensitive paths.
