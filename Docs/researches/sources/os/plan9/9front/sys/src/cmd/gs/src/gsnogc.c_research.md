# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.c

Implements non-tracing reclamation and string freelists for non-GC Ghostscript environments.

Key behavior:
- Provides unaligned 32-bit get/put helpers matching `SFREE_NB`.
- `sf_alloc_string` scans current chunk string freelist for exact-size reusable blocks for requests >= 40 bytes and below large-object threshold; otherwise delegates to reference memory allocator.
- `sf_free_string` returns strings to chunk storage:
  - immediately moves `ctop` for top-of-string-area frees
  - inserts larger strings into address-ordered freelists
  - inserts tiny strings into per-256-byte one-byte freelists
  - updates lost string accounting and debug-fill patterns
- DEBUG overlap checks detect suspicious freelist insertions.
- `sf_enable_free` delegates enable-free and reinstalls string free hook when enabled.
- `sf_merge_strings` coalesces free strings at the bottom/top boundary of chunk string storage.
- `sf_consolidate_free` closes chunks, merges string space, recovers unused string-marking space, reinitializes freelists, reopens chunks, and consolidates object free space.
- `gs_nogc_reclaim` walks VM spaces, installs string freelist behavior on each distinct reference memory and stable memory allocator, then consolidates.
- `use_string_freelists` rewires allocator string and consolidate procs to no-GC versions.

Dependencies:
- Uses `gxalloc.h` reference-memory internals: chunks, chunk locators, lost accounting, and consolidation helpers.
- Declared through `gsnogc.h` as a VM reclaim procedure.

Research notes:
- This is not a tracing collector; it only coalesces free memory and installs freelist reuse.
- It assumes environments without save/restore and without real garbage collection needs.
