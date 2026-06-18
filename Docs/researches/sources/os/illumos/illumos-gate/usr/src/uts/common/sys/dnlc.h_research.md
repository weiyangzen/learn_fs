# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dnlc.h

## Scope

Complete file read, 383 lines. This header defines the Directory Name Lookup Cache and large-directory cache interfaces.

## Public Surface

For the standard DNLC it defines:

- `ncache_t`: hash-chain entry mapping parent vnode and name to target vnode.
- `NCACHE_SIZE(namelen)`.
- `nc_hash_t`: hash bucket with lock.
- Deprecated `struct ncstats`.
- Preferred `struct nc_stats` kstat counters shared with directory caching.
- `DNLCHASH(name, dvp, hash, namlen)`.

Under `_KERNEL` or `_FAKE_KERNEL`, it declares `ncsize`, `negative_cache_vnode`, `DNLC_NO_VNODE`, and DNLC functions for init, enter, update, lookup, purge, purge by vnode/vfs/vnodeops, remove, and cache reduction.

For directory caching it defines:

- `dcfree_t`, `dcentry_t`, `DCENTTRY_SIZE()`, `dircache_t`, `dcanchor_t`, and `dchead_t`.
- Kernel-only `dcret_t` result enum.
- Directory cache functions for start, add entry/free space, complete, purge, lookup, update, remove entry/free space, anchor init/fini.

## Behavior And Integration

The standard DNLC caches recent parent-vnode/name to vnode mappings, including negative entries via `DNLC_NO_VNODE`. The directory cache supports whole-directory caching for large directories with filesystem-supplied handles for entries and free space.

## Dependencies And Invariants

`ncache_t.namlen` and `dcentry_t.de_namelen` are `uchar_t`, so names must fit below 256 bytes excluding null. `DNLCHASH` asserts this. `dcanchor_t.dca_lock` protects the cache pointer.

## Risks

The macro `DCENTTRY_SIZE` appears misspelled with three `T` characters; callers must use the actual exported spelling. Directory caches can be purged due to memory pressure at any time, so filesystems must treat `DNOCACHE`/`DNOMEM` as normal outcomes.
