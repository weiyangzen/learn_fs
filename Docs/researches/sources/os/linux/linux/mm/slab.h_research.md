# File Research: sources/os/linux/linux/mm/slab.h

Internal slab allocator header shared by SLUB/slab support code. It defines the in-memory layout of `struct slab`, core `struct kmem_cache` fields, kmalloc cache lookup helpers, debug/metadata helpers, and internal allocator entry points.

Key responsibilities:
- Defines freelist/counter packing for lockless slab freelist updates, including optional wide compare-exchange support to avoid ABA problems.
- Defines `struct slab`, which overlays selected `struct page` fields, with static assertions to keep the layout compatible.
- Provides conversion helpers between slab, folio, page, virtual address, node id, pgdat, order, size, and object index.
- Defines `struct kmem_cache` internal fields for flags, object sizes, free-pointer offset, sheaf capacity, order/object packing, constructor, alignment, redzone padding, sysfs/debug/randomization/KASAN/usercopy/stat fields, and per-node pointers.
- Provides `cache_has_sheaves()` and sysfs support stubs/entry points for configurations that support slab sysfs.
- Provides nearest-object and object-index helpers used by debugging, reporting, and object validation.
- Declares allocator lifecycle state (`enum slab_state`), global slab mutex/list/cache variables, kmalloc cache metadata, and boot/cache creation functions.
- Implements `kmalloc_slab()` to map requested allocation size, kmalloc bucket set, GFP flags, and caller into the appropriate kmem cache.
- Declares cache creation, merging, flag normalization, shutdown, shrink, release, and slabinfo functions.
- Defines slab debug flag helpers, KUnit hook stubs, KASAN/KMSAN metadata access suppression helpers, and SLUB debug/stat prototypes.
- Defines slab object extension helpers under `CONFIG_SLAB_OBJ_EXT`, including object-extension pointer decoding, stride handling, and indexed extension access.
- Declares memcg slab post-alloc/free hooks, RCU free helpers, large-kmalloc size/order helpers, unreclaimable slab dump hooks, heap object checking, deferred free barriers, and object info diagnostics.

Important behavior:
- `struct slab` deliberately reuses `struct page` storage. Compile-time assertions enforce field offsets and total size, so allocator code can safely reinterpret the first page of a slab folio as `struct slab`.
- ABA-resistant freelist updates are only enabled when the architecture provides the required wide cmpxchg and aligned `struct page` support.
- `page_slab()` checks the page type marker on the compound head and returns NULL for non-slab pages, including large kmalloc pages that are not ordinary slab objects.
- `slab_folio()` is the preferred abstraction for converting a slab to its backing folio, keeping callers away from direct casts.
- `kmalloc_slab()` uses the small-size index table for allocations up to 192 bytes and `fls(size - 1)` for larger kmalloc cache indexes.
- Metadata access helpers disable KASAN/KMSAN while allocator internals touch memory outside the logical allocated object.
- Object extensions are not refcounted; `get_slab_obj_exts()`/`put_slab_obj_exts()` instead bracket sanitizer suppression while callers inspect extension arrays.
- Init-on-alloc/free decisions avoid constructors and avoid unconditional clearing for `SLAB_TYPESAFE_BY_RCU` or poisoned caches unless the caller explicitly requested zeroing.

Dependencies:
- Depends on slab public APIs, folios/pages, memcontrol, list_lru, local locks, randomization, sysfs/kobjects, KFENCE, KASAN/KMSAN, hardened usercopy, debugfs, SLUB debug, KUnit, kmalloc bucket definitions, and architecture cmpxchg capabilities.

Notable risks:
- Layout coupling to `struct page` is intentionally strict; any page/slab field change must preserve asserted offsets or update the overlay design.
- Freelist hardening, randomization, object extensions, memcg metadata, and sanitizer suppression all interact with allocator hot paths, so helper misuse can become either a correctness bug or a performance regression.
- `kmalloc_slab()` assumes callers already validated nonzero size and maximum size.
- Object-extension pointer flags and memcg data bits share storage; the validation in `slab_obj_exts()` is important for catching invalid mixed states.
