# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_handle.c

## Purpose

This file implements MDCACHE object-handle operations for namespace, attributes, references, wire/key conversion, pNFS layouts, and export-level handle creation. It is the main bridge between upper FSAL object ops and lower sub-FSAL handles. The source was read as a complete 1711-line file.

## Important APIs, Types, and Functions

Key functions include `mdcache_alloc_and_check_handle`, `mdcache_lookup`, `mdcache_mkdir`, `mdcache_mknode`, `mdcache_symlink`, `mdcache_readlink`, `mdcache_link`, `mdcache_readdir`, `mdcache_test_access`, `mdcache_rename`, `mdcache_refresh_attrs`, `mdcache_getattrs`, `mdcache_setattr2`, `mdcache_unlink`, handle digest/key/cmp wrappers, pNFS layout wrappers, ref/release methods, `mdcache_merge`, `mdcache_is_referral`, `mdcache_handle_ops_init`, `mdcache_lookup_path`, and `mdcache_create_handle`.

## Control Flow

Create operations call the sub-FSAL, request non-ACL attributes, then under parent content lock allocate/check an MDCACHE entry and optionally add a chunked dirent. Lookup delegates to `mdc_lookup`. Readdir either passes through uncached or uses chunked MDCACHE readdir based on `get_readdir_mode`. Rename checks destination cache/delegations, locks source and destination in stable order, performs sub-FSAL rename, invalidates affected attrs/dirents, handles FSALs whose rename changes keys, and marks overwritten entries unreachable. Getattr uses cache validity under `attr_lock`, refreshes from the sub-FSAL on misses, and may invalidate directory dirents when mtime changes.

## State and Persistence Behavior

The file manages in-memory MDCACHE entries, attr caches, content trust, parent pointers, dirents, export references, LRU refs, and unreachable/stale markers. Backing filesystem persistence is always performed by the sub-FSAL.

## Dependencies and Integration Points

It depends on MDCACHE LRU/hash/AVL helpers, FSAL default ops, NFS ACL/export/state helpers, dynamic metrics, sub-FSAL object and export ops, and xattr wrappers registered in `mdcache_handle_ops_init`.

## Risks and Edge Cases

Lock ordering is central: parent content locks, source/destination directory locks, and attr locks must not conflict with LRU cleanup. Attribute cache generation can change during refresh and must clear trust. Rename over junctions is blocked; rename-changing-key FSALs require invalidation and unreachable marking. Owner-skip access can use cached owner by configuration, trading correctness risk for speed.

## Test Signals

Exercise lookup/create/link/rename/unlink with chunked and uncached readdir modes, stale sub-FSAL responses, directory parent changes, delegation conflicts, attr cache hit/miss metrics, ACL/FS_LOCATIONS/security-label refresh, referral cache updates, pNFS layout pass-through, ref/put/release behavior, and create-handle lookup from host handles.
