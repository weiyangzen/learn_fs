<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.h -->
# sources/test-tools/strace/src/mmap_cache.h

Purpose: declares mmap-cache data structures and lookup APIs.
Important APIs/types/functions: `MMAP_CACHE_PROT_*` flags, `struct mmap_cache_entry_t`, `struct mmap_cache_t`, `mmap_cache_rebuild_result`, `mmap_cache_search_fn`, and public enable/rebuild/search functions.
Control flow: header only; callers use rebuild result to decide whether cache is ready, renewed, or unavailable. State and persistence behavior: defines per-tcb cache layout and free callback slot.
Dependencies and integration points: stack tracing and `mmap_cache.c`. Risks: structure layout changes must match allocation/free logic. Test signals: compile coverage plus cache lifecycle tests through public functions.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.h -->
