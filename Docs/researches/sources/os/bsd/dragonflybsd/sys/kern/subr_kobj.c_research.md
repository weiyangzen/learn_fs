# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_kobj.c

## Summary
Implements DragonFly’s kernel object method dispatch support: class compilation, method lookup/cache, object creation, and class reference lifetime.

## Main Responsibilities
- Initializes the global `kobj_token` at boot.
- Assigns descriptor IDs for method cache indexing.
- Compiles `kobj_class_t` classes into `kobj_ops` cache tables.
- Resolves methods through class methods, recursive base classes, or descriptor defaults.
- Provides cached dispatch via `kobj_lookup_method_cache()`.
- Creates, initializes, and deletes kobj instances with class refcounting.

## Important Behavior
Each compiled class gets a cache initialized to a null method. The cache slot is selected by `desc->id & (KOBJ_CACHE_SIZE - 1)`, and misses fall back to full method lookup. Class compile has a preemption race guard: if another thread compiled first, the extra table is freed.

## Risks
Descriptor unregister is a stub. Class uninstantiate frees ops when refs reach zero, so object lifetime must match class refcounts. Base-class search order is recursive and first-match.
