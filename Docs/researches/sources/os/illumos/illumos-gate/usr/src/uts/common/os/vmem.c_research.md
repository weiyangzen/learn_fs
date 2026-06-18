# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vmem.c

Implements the illumos virtual memory/resource arena allocator (`vmem`), a hierarchical allocator for kernel virtual addresses, identifiers, and other integer ranges.

Key responsibilities:
- Creates and destroys arenas with optional imported spans from source arenas.
- Represents arena contents as spans and allocated/free segments.
- Provides fast unconstrained allocation, constrained allocation, next-fit, first-fit, best-fit, end allocation, and quantum cache acceleration.
- Tracks allocated segments in per-arena hash tables and free segments in power-of-two freelists.
- Preallocates `vmem_seg_t` metadata to avoid recursive allocation deadlocks.
- Exports arena walking, sizing, containment checks, kstats, periodic hash resizing, and qcache reaping.

Important structures and concepts:
- `vmem_t` arenas form parent/child trees through source allocation/free functions.
- `vmem_seg_t` entries are linked in arena order and also in next-of-kin lists for allocation hash chains, freelists, or span marker lists.
- Span markers bound coalescing and allow whole imported spans to be returned to the source when fully free.
- Free lists use size-class markers and a bitmap-like `vm_freemap` for quick discovery of non-empty size classes.
- Small allocations can bypass vmem segment management through per-size kmem quantum caches.

Important paths:
- `vmem_span_create()` inserts a span marker and an initial free segment, updating import and total-memory kstats.
- `vmem_seg_alloc()` carves an allocation out of a free segment, splitting left/right/middle remainders as needed and hashing the allocated segment.
- `vmem_xalloc()` validates alignment/phase/nocross constraints, searches freelists for a suitable segment, imports from the source arena if needed, handles source over-import cleanup, and panics for mandatory `VM_PANIC` allocation failures.
- `vmem_alloc()` serves qcache-sized allocations through kmem caches, delegates constrained policies to `vmem_xalloc()`, and otherwise performs instant-fit freelist allocation.
- `vmem_xfree()` removes the allocated segment from the hash, coalesces neighbors, returns whole imported spans to the source, or reinserts the coalesced free segment.
- `vmem_nextfit_alloc()` advances a rotor through the arena to reduce address reuse and support cycling identifier allocation.
- `vmem_populate()` refills per-arena segment reserves from a global freelist or `vmem_seg_arena`, using separate locks for sleep, nosleep, pushpage, and panic contexts.
- `vmem_create_common()` initializes arena metadata, qcache caches, kstats, source links, populator state, and optional initial spans.
- `vmem_update()` periodically broadcasts arena condition variables and rescales allocation hash tables.
- `vmem_init()` bootstraps the heap arena and metadata arenas (`vmem_metadata`, `vmem_seg`, `vmem_hash`, `vmem_vmem`) from static early storage.

Locking and reliability:
- Each arena has a single `vm_lock`; hot arenas are expected to use quantum caching for scalability.
- Segment metadata reserves are carefully sized to handle worst-case import and allocation recursion.
- Allocation failure injection is supported through `vmem_mtbf` and per-arena `vm_mtbf`.
- Hash-delete failures or wrong-size frees panic, providing runtime sanity checking even without full kmem debug features.

Filesystem relevance:
- Indirect but foundational. VFS, filesystems, VM, device mappings, buffer mapping, and kernel heap consumers use vmem-backed arenas to allocate address ranges and identifiers. The legacy `rmap` wrapper elsewhere also builds on vmem.
