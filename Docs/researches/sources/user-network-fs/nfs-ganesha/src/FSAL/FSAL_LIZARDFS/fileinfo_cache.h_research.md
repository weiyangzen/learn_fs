# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/fileinfo_cache.h

Purpose: Declares the LizardFS fileinfo cache used by the pNFS DS implementation to reuse `liz_fileinfo_t` objects by inode.

Important APIs and types: Opaque types are `liz_fileinfo_cache_t` and `liz_fileinfo_entry_t`. Functions create/reset/destroy the cache, acquire/release/erase entries, pop expired entries, free entries, extract fileinfo from an entry, and attach fileinfo to an entry.

Control flow: DS code acquires a cache entry for an inode. If `liz_extract_fileinfo()` returns null, it opens the file and calls `liz_attach_fileinfo()`. On DS handle release it calls `liz_fileinfo_cache_release()`. Cache drains use `liz_fileinfo_cache_pop_expired()` followed by `liz_extract_fileinfo()`, LizardFS release, and `liz_fileinfo_entry_free()`.

State and persistence: Cache state is opaque and configured by max entries plus minimum timeout. It stores references to LizardFS fileinfo handles, not file data. Entries may be retained after release until eviction timeout.

Dependencies and integration: The header uses the LizardFS C API and is included by `lzfs_internal.h`, making the cache part of the FSAL private ABI. Implementation is outside the requested files, likely supplied by the LizardFS client library or another source unit.

Risks: Lifetime semantics are subtle: acquired entries must be released or erased; popped expired entries must be freed after releasing their fileinfo; attached fileinfo must not be double-released. Cache fullness returns null from acquire, which DS maps to I/O failure. Timeout units differ between API docs and export config, requiring correct seconds-to-ms conversion.

Test signals: Cache acquire/release balance, erase on open failure, expiration drain, max-size pressure, concurrent acquire of same inode, export teardown drain, and valgrind/ASAN leak checks during pNFS DS workloads.
