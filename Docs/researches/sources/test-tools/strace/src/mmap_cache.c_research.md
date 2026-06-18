<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.c -->
# sources/test-tools/strace/src/mmap_cache.c

Purpose: maintains a per-tracee cache of `/proc/PID/maps` for stack tracing and address-to-mapping lookups.
Important APIs/types/functions: `mmap_cache_enable`, `mmap_cache_rebuild_if_invalid`, `mmap_cache_search`, `mmap_cache_search_custom`, `delete_mmap_cache`, `mmap_notify_register_client`, and `struct mmap_cache_t`.
Control flow: global generation is incremented by mmap notifications; stale per-tcb caches are freed; rebuild parses maps lines, validates permission fields, skips duplicates/overlaps, grows entries, and installs the cache. Search uses binary lookup over sorted ranges.
State and persistence behavior: global generation plus per-`tcb` allocated cache with free callback. Dependencies and integration points: `/proc`, mmap notification hooks, stack trace code, and large-file wrappers.
Risks: maps parsing and overlap handling affect symbolization; stale cache invalidation is critical after mapping-changing syscalls. Test signals: cache rebuild/search tests, mmap/munmap invalidation, duplicate vsyscall entries, and malformed maps lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmap_cache.c -->
