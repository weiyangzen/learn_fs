# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_helpers.c

## Purpose
`mdcache_helpers.c` implements the central helper behavior for the MDCACHE stackable FSAL: cache-entry creation, keyed lookup, export mapping, parent-handle caching, directory-entry caching, chunked and uncached readdir, and final invalidation/attribute update helpers. It is the main bridge between lower FSAL object handles and the in-memory MDCACHE entry model.

## Important APIs, Types, and Functions
- `mdcache_new_entry()` creates or finds an MDCACHE entry for a lower FSAL handle, handles hash races, initializes directory/file state, copies attributes, inserts the entry into LRU, and releases duplicate lower handles through `merge()`/`release()`.
- `mdcache_find_keyed_reason()` looks up a cache key in the cache inode hash, takes an LRU reference, and ensures the active export mapping is valid.
- `mdcache_locate_host()` converts a host handle into a lower-FSAL key, tries the cache, otherwise creates a lower handle and caches it.
- `mdc_lookup()` and `mdc_lookup_uncached()` implement name lookup, including cached dirent lookup, negative-cache trust, lower-FSAL lookup on miss, and parent `..` special handling.
- `mdcache_dirent_add()`, `mdcache_dirent_remove()`, `place_new_dirent()`, `mdcache_dirent_invalidate_all()`, and `mdcache_clean_dirent_chunk()` maintain directory AVL indexes, chunk lists, detached dirent LRU lists, and trust flags.
- `mdcache_readdir_uncached()`, `mdcache_populate_dir_chunk()`, and `mdcache_readdir_chunked()` drive directory enumeration with either direct lower-FSAL callbacks or chunked cache population.
- `mdc_check_mapping()`, `mdc_clean_entry()`, `mdc_get_parent()`, and `mdc_get_parent_handle()` manage per-export entry ownership and cached parent handles.
- `_mdcache_kill_entry()` removes an entry from the cache hash and queues deferred cleanup if outstanding references remain.
- `mdc_update_attr_cache()` preserves and replaces owned ACL, fs_locations, and sec_label payloads while updating trust metadata.

## Control Flow
Cache entry creation starts by deriving a lower-FSAL key from `handle_to_key()`, probing the cache hash, then allocating/reusing an LRU entry only after a cache miss. The final insertion is protected by a cache hash latch so racing creators either win insertion or discard their provisional entry and merge the lower-FSAL handle into the existing object.

Lookup first tries cached directory content under `content_lock`. If the dirent cache is trusted, `mdc_try_get_cached()` resolves by cached key and can serve negative results when the directory is marked fully populated and export options allow negative cache trust. On stale/missing cache state and when uncached lookup is allowed, the path upgrades to a write lock, invalidates stale dirent structures if needed, calls the lower FSAL `lookup()`, and caches the result.

Chunked readdir keeps a directory content lock while walking resident chunks. Missing chunks are populated through lower-FSAL `readdir()` callbacks that create MDCACHE entries and dirents. The code handles readahead, gaps, chunk collisions, reloads when keyed entries are missing, and FSALs whose readdir cursor is a name rather than an opaque cookie. The callback path avoids promoting scan-created entries into the hot LRU path, preserving scan resistance.

Entry cleanup removes all export mappings under the documented lock order, invalidates directory content, removes hash-table membership, releases owned attributes/keys, and leaves final object release to LRU cleanup.

## State and Persistence Behavior
All cache state is in memory. Persistent filesystem state is not changed except via lower-FSAL calls made elsewhere; this file caches metadata and object identity. `mde_flags` track trust in attributes, ACLs, content, directory chunks, fs_locations, sec_label, and unreachable state. Directory state includes AVL trees by name, cookie, and sorted cookie order, resident `dir_chunk` lists, detached dirents, parent host-handle cache, and `first_ck`. Parent handles expire according to lower export parent-expire policy. Attribute timestamps and `expire_time_attr` govern cache validity.

## Dependencies and Integration Points
This file depends on `mdcache_lru` for entry/chunk references and recycling, `mdcache_hash` for keyed entry lookup, `mdcache_avl` for dirent indexes, `fsal_commonlib` and lower-FSAL object/export ops for handle conversion, lookup, readdir, release, merge, and close, plus SAL state helpers and dynamic metrics. `subcall` and `supercall` macros from `mdcache_int.h` switch `op_ctx->fsal_export` between MDCACHE and the lower FSAL.

## Risks and Edge Cases
The main risks are lock-order regressions, reference leaks across chunk population, stale export mappings during unexport, FSAL cookie collisions, name/cookie inconsistencies in fast-mutating directories, and incorrect trust-flag transitions. Readdir paths are especially sensitive: dropping `content_lock` can invalidate dirent/chunk pointers, whence-is-name mode may force rescans, and chunk reload logic must avoid double-unref or stale `mde_entry` references. Attribute update code must preserve ownership of ACL/fs_locations/sec_label payloads exactly once.

## Test Signals
Useful tests include concurrent lookup/create races for one object, unexport while handles are being looked up, readdir of large and mutating directories with chunking enabled, FSALs with and without `fso_compute_readdir_cookie` and `fso_whence_is_name`, negative lookup caching under trusted and untrusted directory states, stale lower handles during readdir, ACL/fs_locations/sec_label refreshes, and parent `..` lookup across export roots.
