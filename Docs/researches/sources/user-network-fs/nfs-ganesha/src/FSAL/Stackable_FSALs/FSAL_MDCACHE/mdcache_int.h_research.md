# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_int.h

## Purpose
`mdcache_int.h` is the internal contract for the MDCACHE FSAL. It defines the cache entry, export wrapper, cache key, LRU metadata, directory chunk/dirent structures, trust flags, stackable-FSAL call macros, helper prototypes, and inline cache-validity utilities used by the MDCACHE implementation.

## Important APIs, Types, and Functions
- `struct mdcache_fsal_export` wraps `struct fsal_export`, stores MDCACHE upcall vectors, export entry lists, unexport flags, dirmap state, and cleanup counters.
- `mdcache_key_t` combines a hash value, lower FSAL identity, and lower-FSAL handle bytes; `mdcache_key_cmp()` orders keys by hash, length, FSAL pointer, and bytes.
- `mdcache_lru_t` stores queue membership, refcounts, active-refcounts, lane, flags, and confounder for both entries and chunks.
- `struct mdcache_fsal_obj_handle` is the cache entry: FSAL object handle, lower handle, attributes/timestamps, hash key, export mappings, LRU state, content lock, and type-specific state.
- `struct dir_chunk` and `mdcache_dir_entry_t` model chunked directory cache content.
- Inline helpers include `test_mde_flags()`, `mdc_export()`, `mdc_cur_export()`, `mdcache_key_dup/delete()`, parent-handle helpers, `mdc_fixup_md()`, `mdcache_test_attrs_trust()`, `mdcache_is_attrs_valid()`, `mdc_has_state()`, and `mdc_unreachable()`.
- Function prototypes expose lookup, readdir, object creation, I/O, xattr, handle ops, export ops, and upcall initialization.

## Control Flow
The header defines the state model used by other files rather than executing a top-level flow. The key inline paths are attribute refresh and validation: `mdc_fixup_md()` sets trust flags and refresh times based on requested and valid masks, while `mdcache_is_attrs_valid()` checks trust, valid bits, expiry, directory invalidation policy, and delegation conditions before allowing cached attributes to satisfy a request.

The stackable FSAL macros redirect `op_ctx->fsal_export` for lower-FSAL calls (`subcall*`) and for callbacks back into the upper layer (`supercall*`). Entry removal flow is also encoded here: `mdc_unreachable()` kills an entry immediately when it has no state, otherwise marks it `MDCACHE_UNREACHABLE` for later cleanup.

## State and Persistence Behavior
All structures represent volatile in-memory cache state. Entry state persists only for the lifetime of the Ganesha process or until LRU/unexport invalidation. The header documents lock ownership: `attr_lock` protects attributes, export mappings, and attribute times; `content_lock` protects directory/symlink cached content; LRU metadata has its own lane locking; `mde_flags` are updated atomically. Directory parent host handles and attribute timestamps are cached with expiry.

## Dependencies and Integration Points
The header includes FSAL, SAL state, upcall, conversion, display, and utility headers. It is consumed by MDCACHE helpers, LRU, main module wiring, config, upcall handling, and handle/export ops outside this subset. The prototypes connect this subset to other MDCACHE files such as open/read/write, xattr, export ops, AVL/hash logic, and NFS state/delegation code.

## Risks and Edge Cases
Because this header defines shared invariants, mismatches in lock discipline or refcount assumptions can corrupt many call paths. Risks include comparing FSAL pointers as key-order components, stale `first_export_id`, incorrect attribute trust when `expire_time_attr` is zero, parent-handle lifetime errors, and state-bearing unreachable entries that must not be freed prematurely.

## Test Signals
Test signals include assertions or stress tests for attr/content lock order, cache-key ordering and duplication/freeing, attribute validity with ACL/fs_locations/sec_label masks, directory parent expiration, unreachable entries with open/lock/delegation state, and stackable FSAL context restoration around nested lower-FSAL and upper-layer callbacks.
