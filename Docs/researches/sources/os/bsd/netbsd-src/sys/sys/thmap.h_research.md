# File Research: sources/os/bsd/netbsd-src/sys/sys/thmap.h

Read completely: 62 lines.

Declares a kernel-only transactional/hash map style interface.

Key elements:
- Explicitly rejects userland inclusion.
- Opaque type `thmap_t` hides implementation.
- Flags include `THMAP_NOCOPY` and `THMAP_SETROOT`.
- `thmap_ops_t` supplies allocator/free callbacks.
- API covers create/destroy, get/put/delete by key bytes, staged garbage collection, root set/get, and final GC.

Risks and notes:
- Ownership and reclamation are central: callers must coordinate `thmap_stage_gc()` and `thmap_gc()`.
- Root handling through `uintptr_t` is intentionally low-level and implementation-coupled.
