# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_slaballoc.c

## Purpose

`kern_slaballoc.c` implements DragonFlyBSD's kernel malloc slab allocator. It provides per-CPU zone-backed small allocations, direct VM-backed oversized allocations, malloc type accounting, dynamic malloc pool management, remote-free handling, string duplication helpers, slab cleanup, and low-level wired kernel-memory allocation/free routines.

## Allocator Model

- Zone sizing:
  - `kmeminit()` chooses `ZoneSize`, `ZoneLimit`, `ZoneMask`, and `ZonePageCount` from memory/KVA limits and creates `ZeroPage`.
  - `kmemfinishinit()` adjusts free-zone release thresholds after CPU count is known.
  - `zoneindex()` maps requested sizes to chunk classes from 8-byte granularity up through the configured zone limit.
  - Power-of-two and cache-aligned requests are rounded/aligned to preserve expected kernel malloc alignment behavior.
- Per-CPU state:
  - `slab_gdinit()` initializes each CPU's slab queues.
  - Each CPU has zone lists by size, free whole-zone lists, delayed oversized-free lists, and a sliding initial chunk index to distribute cache use.
- Malloc type state:
  - `malloc_init()` initializes a `malloc_type`, default limit, optional object-size management, per-CPU usage array, and global `kmemstatistics` linkage.
  - `malloc_uninit()` drains pending IPIs, removes the type from stats, checks outstanding allocations under invariants, and tears down object management.
  - `malloc_reinit_ncpus()` expands early single-CPU usage arrays after SMP count is known.
  - `kmalloc_raise_limit()`, `kmalloc_set_unlimited()`, `kmalloc_create()`, `_kmalloc_create_obj()`, and `kmalloc_destroy()` manage dynamic pools.

## Allocation And Free Paths

- `_kmalloc()`:
  - Handles malloc type limits with loose per-CPU accounting.
  - Returns a special non-NULL `ZERO_LENGTH_PTR` for size-zero allocations.
  - Performs hysteresis cleanup of previously free zones and delayed oversized frees when blocking is allowed.
  - Sends large or page-multiple allocations directly to `kmem_slab_alloc()`.
  - Allocates small chunks from local free lists, never-used zone space, reused whole zones, or newly allocated zones.
  - Updates per-CPU allocation counts and memory usage, optionally zeroes or pattern-fills under invariants, and records KTR memory events.
- `krealloc()`:
  - Reuses the existing allocation if the oversized rounded size or slab chunk class still fits.
  - Otherwise allocates, copies up to old usable size, and frees the old pointer.
- `kmalloc_usable_size()` reports page-rounded oversized allocation size or slab chunk size.
- `_kfree()`:
  - Rejects NULL, ignores the zero-length sentinel, and validates malloc type magic.
  - Frees oversized allocations immediately or defers them on per-CPU `FreeOvZones` when in interrupt-sensitive context.
  - For remote slab frees, links chunks into the owning zone's `z_RChunks`, uses `z_RSignal`/`z_RCount` to prevent zone teardown races, and sends passive IPIs only when needed.
  - For local frees, marks the chunk free, optionally writes invariant debug patterns, returns it to the local free list, updates stats, and moves whole-free zones to `FreeZones`.
- `kfree_remote()` drains remote-freed chunks on the owning CPU and restores zones to active/free lists.
- `slab_cleanup()` periodically drains remote chunks and moves fully free zones to the free list.

## Low-Level VM Backend

- `kmem_slab_alloc()` reserves kernel map space, inserts wired kernel-object mappings, allocates VM pages with flags derived from malloc flags, handles blocking/nonblocking allocation, maps pages into the kernel pmap, zeroes if requested, and invalidates TLBs.
- `kmem_slab_free()` removes the kernel map range for a VM-backed slab/oversized allocation.

## Debugging And Instrumentation

The file defines common malloc types (`M_CACHE`, `M_DEVBUF`, `M_TEMP`, `M_DRM`, IPv6 types), KTR memory events, invariant-only allocation/free bitmaps, optional malloc pattern fill, optional freed-memory weird pattern fill, `SLAB_DEBUG` allocation source recording, and a slow `kmalloc_poller` kthread that polls malloc object managers.

## Risks And Invariants

The allocator intentionally avoids locks on the hot path by relying on per-CPU ownership and critical sections. Remote free correctness depends on not dereferencing a zone after publishing a chunk to `z_RChunks` unless `z_RCount` has protected it. Free paths avoid blocking because they may run from IPIs or interrupt-sensitive contexts; VM map cleanup is shifted to allocation or polling paths. `btokup()` page-count metadata distinguishes oversized allocations from CPU-owned zones and is central to both free and usable-size behavior.
