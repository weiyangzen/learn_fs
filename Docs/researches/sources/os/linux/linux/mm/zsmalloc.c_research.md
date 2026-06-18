# File Research: sources/os/linux/linux/mm/zsmalloc.c

## Purpose

`zsmalloc.c` implements the zsmalloc allocator, a compact allocator for compressed objects that are typically smaller than a page and may span page boundaries. It is used by zswap and zram-like compressed-memory users. The allocator groups physical pages into zspages, divides each zspage into fixed-size chunks by size class, tracks fullness for allocation and compaction, and supports page migration through movable operations.

## Core Data Structures

- `struct zs_pool` is a named allocator pool with size-class table, allocated-page count, compaction stats, shrinker, optional debugfs stats, deferred free work, pool migration lock, and compaction-in-progress guard.
- `struct size_class` owns one allocation size, zspage geometry, fullness lists, a spinlock, and class stats.
- `struct zspage` describes a chain of one or more `zpdesc` pages: class index, fullness group, in-use count, free-object head, first descriptor, pool pointer, list node, and custom read/write lock.
- `struct link_free` is embedded in free chunks and stores either the next free object index or the allocated object's handle.

Handles point to separately allocated `zs_handle` objects. The handle stores an encoded object location composed of PFN and object index. Allocated chunk headers store the handle with `OBJ_ALLOCATED_TAG`; huge single-object zspages store the handle in the first zpdesc.

## Size Classes And Fullness

Objects are aligned to `ZS_ALIGN`, include `ZS_HANDLE_SIZE` overhead, and are capped at `ZS_MAX_ALLOC_SIZE == PAGE_SIZE`. Size classes are derived from `ZS_MIN_ALLOC_SIZE`, `ZS_SIZE_CLASS_DELTA`, and `CLASS_BITS`. During pool creation, adjacent logical classes can share one `size_class` if they have the same `pages_per_zspage` and `objs_per_zspage`, reducing metadata.

Fullness groups range from empty to 10 percent bands through 99 percent and 100 percent. Allocation searches high-utilization groups first via `find_get_zspage()`, while compaction chooses sparse source pages and dense destination pages.

## Allocation And Free

`zs_malloc()` validates size, allocates a handle, finds the size class, and tries to allocate from an existing zspage. If none is available, it allocates a new zspage, initializes its free list, inserts it into the correct fullness group, marks pages movable when compaction is enabled, updates stats, and returns the handle.

`obj_malloc()` removes the first free object from the zspage free list, writes the tagged handle into the object header or huge-page descriptor, records the encoded object location in the handle, and increments `zspage->inuse`.

`zs_free()` resolves the handle to a zspage under `pool->lock`, locks the class, clears the object back to the free list with `obj_free()`, updates fullness and stats, and frees the whole zspage if it becomes empty. `free_zspage()` tries to lock all component pages; if it cannot do so from the non-sleepable free path, it schedules deferred free work.

## Object Access APIs

The exported access APIs are:

- `zs_obj_read_begin()` / `zs_obj_read_end()`
- `zs_obj_read_sg_begin()` / `zs_obj_read_sg_end()`
- `zs_obj_write()`

They resolve the handle under the pool read lock, acquire a zspage read lock to prevent migration, then map or copy the object. Objects fully contained in one page can be accessed by local kmap or a single scatterlist entry; cross-page objects are copied through a caller-provided buffer or represented as a two-entry scatterlist.

## Compaction And Migration

`zs_compact()` serializes pool compaction with `compaction_in_progress`, iterates size classes, and calls `__zs_compact()`. Compaction isolates a dense destination zspage and sparse source zspages, write-locks source zspages, migrates allocated objects with `migrate_zspage()`, frees empty source zspages, and periodically drops locks if the pool lock is contended.

`migrate_zspage()` finds allocated objects, allocates corresponding slots in the destination, copies object bytes with `zs_object_copy()`, updates handles to point at new object locations, and frees old object slots.

With `CONFIG_COMPACTION`, zsmalloc registers `zsmalloc_mops`:

- `zs_page_isolate()` accepts only still-live zsmalloc pages.
- `zs_page_migrate()` copies an individual physical page to a new page, updates every allocated handle on that subpage, replaces the subpage in the zspage chain, transfers zsmalloc/movable metadata, adjusts `NR_ZSPAGES` zone stats if the zone changes, and clears the old descriptor.
- `zs_page_putback()` is a no-op.

The custom `zspage_lock` allows sleeping readers and atomic trylock writers. This protects object access from migration while avoiding non-preemptible long read sections during compression or decompression users.

## Shrinker, Stats, And Lifecycle

`zs_register_shrinker()` installs a shrinker that estimates compactable pages with `zs_can_compact()` and frees pages through `zs_compact()`. Optional `CONFIG_ZSMALLOC_STAT` debugfs output exposes per-class fullness, allocation, usage, pages, and freeable counts under `zsmalloc/<pool>/classes`.

`zs_create_pool()` allocates the pool, builds size classes, initializes fullness lists, creates debugfs stats, and registers the shrinker. `zs_destroy_pool()` unregisters the shrinker, flushes deferred migration/free work, destroys debugfs stats, warns if fullness lists are not empty, and frees classes and pool metadata. Module init creates handle and zspage caches and registers movable page operations; exit undoes those registrations.

## Integration Points

The allocator exports pool creation/destruction, allocation/free, object read/write, compaction, total page count, huge-class size, size-class lookup, and stats. `zswap.c` uses zsmalloc pools for compressed page storage, and `vmstat.c` exposes `NR_ZSPAGES` when zsmalloc is enabled.

## Concurrency And Invariants

- Lock order is page lock, pool lock, class lock, zspage lock.
- `class->lock` protects fullness lists, class stats, and object allocation/free in a zspage.
- `pool->lock` protects races between handle resolution, migration, and free.
- Empty zspages can only be destroyed when all component pages are locked.
- Handles must be updated before old object storage is freed during compaction or page migration.
- `PageZsmalloc` remains sticky until the page returns to the buddy allocator.

## Risks And Test Focus

Risks include handle/object encoding overflow on unusual memory models, cross-page copy bugs, fullness-list stat drift, migration races with readers, deferred free leaks, and pool destruction with live objects. Tests should stress highmem, cross-page object sizes, huge classes, compaction under concurrent allocation/free/read/write, memory hotplug or page migration, shrinker invocation, and debugfs stat consistency.
