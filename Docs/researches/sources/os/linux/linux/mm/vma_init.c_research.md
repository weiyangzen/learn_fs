# File Research: sources/os/linux/linux/mm/vma_init.c

This file provides VMA allocation, duplication, initialization-from-existing, and freeing shared by MMU and NOMMU configurations.

Key elements:
- `vm_area_cachep` is the slab cache for `struct vm_area_struct`.
- `vma_state_init()` creates the `vm_area_struct` cache with hardware-cache alignment, panic-on-failure, RCU type safety, accounting, a free pointer offset at `vm_freeptr`, and sheaf capacity 32.
- `vm_area_alloc()` allocates a VMA from the cache and initializes it with `vma_init(vma, mm)`.
- `vm_area_init_from()` copies the fields needed to duplicate an existing VMA: mm, ops, range, anon_vma, pgoff, file, private data, flags, page protection, shared interval-tree state, userfaultfd context, optional anon name, swap readahead, NOMMU region, NUMA policy, and PFNMAP tracking reset.
- `vm_area_dup()` allocates a duplicate, copies state, duplicates PFNMAP tracking context if present, initializes the VMA lock, anon_vma chain, NUMA balancing state, and anon name.
- `vm_area_free()` asserts the VMA is detached, frees NUMA balancing state, anon name, PFNMAP tracking context, and returns it to the cache.

PFNMAP tracking:
- When `__HAVE_PFNMAP_TRACKING` is enabled, `vma_pfnmap_track_ctx_dup()` increments a kref on the tracking context unless it would overflow.
- `vma_pfnmap_track_ctx_release()` drops the reference and clears the VMA pointer.
- Stub versions are compiled otherwise.

Research notes:
- This file centralizes lifecycle invariants for VMA objects, separating allocation/dup/free mechanics from structural address-space manipulation.
- `vm_area_dup()` does not attach the duplicate into any tree; callers must finish policy/anon_vma/file setup and insert it through VMA APIs.
