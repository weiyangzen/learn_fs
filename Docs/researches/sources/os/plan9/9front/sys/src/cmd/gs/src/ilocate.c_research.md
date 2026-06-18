# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ilocate.c

Implements chunk lookup and debug validation for Ghostscript ref memory.

Key points:
- `gc_locate` locates a pointer in chunks across:
  - current memory
  - stable allocator
  - local/global counterpart space
  - save levels
  - system space
- Used primarily by string GC and debug validation.
- Debug-only validation includes:
  - `ialloc_validate_spaces`
  - `ialloc_validate_memory`
  - `ialloc_validate_chunk`
  - `ialloc_validate_object`
- Temporarily saves allocator state to make current allocation chunks appear valid during validation.
- Validates:
  - freelist object types and sizes
  - object sizes and type descriptors
  - refs and packed refs
  - names and name strings
  - strings
  - arrays, packed arrays, dictionaries
  - struct pointers enumerated through type descriptors
- Optional `IGC_PTR_STABILITY_CHECK` detects references from more stable spaces to less stable spaces.
- Non-debug builds provide no-op validation functions.

Dependencies and interactions:
- Used by `igc.c` and `igcstr.c`.
- Uses `iname.h`, packed-ref utilities, dictionary layout, and allocator/chunk internals.

Research relevance:
- GC support utility for locating referents and diagnosing heap/reference corruption.
