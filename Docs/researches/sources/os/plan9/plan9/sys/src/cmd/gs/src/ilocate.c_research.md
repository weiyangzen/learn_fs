# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ilocate.c

Implements chunk lookup and debug validation for Ghostscript ref memory.

Key points:
- `gc_locate` locates a pointer in chunks across current memory, stable allocators, local/global counterpart spaces, save levels, and system space.
- Used primarily by string GC and debug validation.
- Debug-only validation includes `ialloc_validate_spaces`, `ialloc_validate_memory`, `ialloc_validate_chunk`, and `ialloc_validate_object`.
- Temporarily saves allocator state so current allocation chunks appear valid during validation.
- Validates freelist object types/sizes, object sizes/type descriptors, refs and packed refs, names and name strings, strings, arrays, packed arrays, dictionaries, and struct pointers enumerated by type descriptors.
- Optional `IGC_PTR_STABILITY_CHECK` detects references from more stable spaces to less stable spaces.
- Non-debug builds provide no-op validation functions.

Research relevance:
- GC support utility for locating referents and diagnosing heap/reference corruption.
