# File Research: sources/os/linux/linux/fs/cachefiles/interface.c

## Purpose
Implements the FS-Cache cache-ops interface for CacheFiles objects: allocation, lookup, withdrawal, invalidation, resizing, object xattr commit, and object reference tracing.

## Main Elements
- Object lifetime: `cachefiles_alloc_object()`, `cachefiles_see_object()`, `cachefiles_grab_object()`, and `cachefiles_put_object()`.
- Size management: `cachefiles_adjust_size()` rounds object EOF to the CacheFiles DIO block size and truncates or expands backing files.
- Lookup path: `cachefiles_lookup_cookie()` cooks a key, creates a CacheFiles object, looks up or creates the backing file, adds it to the active object list, and adjusts size.
- Resize path: `cachefiles_resize_cookie()` shrinks backing files with `cachefiles_shorten_object()` or updates cookie size on expansion.
- Cleanup path: `cachefiles_commit_object()`, `cachefiles_clean_up_object()`, and `cachefiles_withdraw_cookie()` commit xattrs, link tmpfiles, delete retired objects, unmark inodes, close files, and drop references.
- Invalidation: `cachefiles_invalidate_cookie()` replaces an object file with a tmpfile, resumes FS-Cache invalidation, and buries the old object.
- `cachefiles_cache_ops`: exports CacheFiles callbacks to FS-Cache.

## Dependencies And Integration
Integrates FS-Cache cookies and volumes with CacheFiles object records, VFS files, xattrs, tmpfiles, name lookup, on-demand object state, and netfs cache-resource operations implemented in `io.c`.

## Risk Notes
Invalidation and withdrawal swap file pointers under `object->lock` while I/O may be active. Tmpfile commit and xattr update determine whether cache content is durable and coherent. Size rounding prevents partial DIO fallback but requires careful truncation/zeroing to avoid stale data exposure.
