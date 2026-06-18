# File Research: sources/os/linux/linux/mm/failslab.c

## Purpose

Provides fault injection for slab allocator failures. It supports global slab failure injection, optional reclaim-GFP filtering, and optional per-cache filtering through `SLAB_FAILSLAB`.

## Configuration State

Static `failslab` contains:

- `struct fault_attr attr`
- `ignore_gfp_reclaim`, default true
- `cache_filter`, default false

Boot setup uses:

- `__setup("failslab=", setup_failslab)`

## Main Function

`should_failslab(struct kmem_cache *s, gfp_t gfpflags)` returns `-ENOMEM` when injection says the allocation should fail, otherwise 0.

It refuses injection when:

- The cache is the bootstrap `kmem_cache`.
- `__GFP_NOFAIL` is set.
- reclaimable allocations are ignored and `__GFP_DIRECT_RECLAIM` is set.
- `cache_filter` is enabled and the cache lacks `SLAB_FAILSLAB`.

If `__GFP_NOWARN` is set, it passes `FAULT_NOWARN` to suppress warning output.

The function is registered with:

- `ALLOW_ERROR_INJECTION(should_failslab, ERRNO)`

## Debugfs Interface

Under `CONFIG_FAULT_INJECTION_DEBUG_FS`, `late_initcall(failslab_debugfs_init)` creates:

- `failslab/ignore-gfp-wait`
- `failslab/cache-filter`

The debugfs root is created via `fault_create_debugfs_attr("failslab", ...)`.
