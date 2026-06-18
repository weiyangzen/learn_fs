# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_file.c

## Purpose

This file implements MDCACHE file I/O object operations. It delegates actual data I/O and locking to the sub-FSAL while keeping MDCACHE metadata validity, async callback context, and created/opened handle wrapping coherent. The source was read as a complete 868-line file.

## Important APIs, Types, and Functions

Important types/functions include `struct mdc_async_arg`, `mdc_set_time_current`, `mdcache_io_advise`, `mdcache_close`, `mdc_open2_by_name`, `mdcache_open2`, `mdcache_check_verifier`, `mdcache_status2`, `mdcache_reopen2`, read/write callback wrappers, `mdcache_read2`, `mdcache_write2`, `mdcache_seek2`, `mdcache_io_advise2`, `mdcache_commit2`, `mdcache_lock_op2`, `mdcache_lease_op2`, `mdcache_close2`, and `mdcache_fallocate`.

## Control Flow

`mdcache_open2` first tries a cached lookup by name and, when possible, opens the existing sub-handle. If not found, it calls parent sub-FSAL `open2`, requests attributes, then wraps the returned sub-handle through `mdcache_alloc_and_check_handle` under the parent content lock. Reads/writes allocate callback wrapper state, call the sub-FSAL async method, then re-enter MDCACHE context through `supercall`. Write-like operations clear `MDCACHE_TRUST_ATTRS` or increment `attr_generation`.

## State and Persistence Behavior

MDCACHE stores no file data. It caches attributes, atime updates after reads, and invalidation flags after write/truncate/commit/fallocate/layout changes. Open/create can create new in-memory MDCACHE entries and dirents.

## Dependencies and Integration Points

The file depends on `mdcache_int.h`, `mdcache_lru.h`, sub-FSAL object ops, FSAL access/state contracts, and handle allocation in `mdcache_handle.c`. Async callbacks integrate lower FSAL completion with upper-layer callback expectations.

## Risks and Edge Cases

Ref handling in async callbacks is subtle: callbacks may drop initial refs, so wrappers take active refs around user callbacks. Stale sub-FSAL results must kill entries. Open-by-name must handle verifier semantics, non-regular targets, and `FSAL_O_TRUNC` invalidation. `Close_Fast` and FD caching behavior is configured elsewhere but affects these paths.

## Test Signals

Test open existing/missing/create guarded/exclusive/unchecked cases, verifier matching, truncation invalidation, async read/write callback ordering and ref safety, stale errors on I/O, commit/fallocate invalidation, close of unreachable last-state entries, and lock/lease pass-through.
