# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_freemap.c

## Purpose
Implements HAMMER2 media allocation and freemap recovery adjustment. It allocates normal data/metadata from bitmap leaves, reserves freemap blocks algorithmically in rotating reserved zones, initializes new freemap leaves, and marks recovered allocations after mount-time repair.

## Allocation State
- `hammer2_fiterate` tracks the preferred allocation offset, next scan offset, loop count, and whether relaxed class allocation has been entered.
- Allocation heuristics are indexed by blockref type and device block radix so different object classes can maintain locality.
- `hmp->freemap_relaxed` allows allocation from any class once stricter class matching has exhausted space.

## Freemap Block Reservation
- `hammer2_freemap_reserve()` handles freemap node/leaf storage. These blocks are not allocated from the freemap; they are placed in reserved 4MB zones at deterministic offsets.
- Existing freemap blocks rotate through eight copies, using the current data offset to choose the next reserved slot.
- The reserved slot depends on freemap level: level 1 leaf, levels 2-5 node, and the corresponding 64KB block inside the reserved segment.

## Normal Allocation
- `hammer2_freemap_alloc()` validates power-of-two allocation sizes, obtains an `mtid`, handles zero-byte allocation by clearing `data_off`, and delegates freemap-node/leaf allocation to the reserve path.
- Normal allocations must be 1KB through 64KB.
- It locks `hmp->fchain`, initializes iteration from the heuristic offset, repeatedly calls `hammer2_freemap_try_alloc()` while it returns EAGAIN, stores the new heuristic offset, and releases fchain.

## Leaf Lookup and Creation
- `hammer2_freemap_try_alloc()` looks up the level-1 freemap leaf covering the next candidate offset.
- If no leaf exists, it creates one through `hammer2_chain_create()`, modifies it, zeros its data, initializes `bigmask` and `avail`, and calls `hammer2_freemap_init()`.
- Existing leaves are skipped early if their `bigmask` says the requested radix cannot fit.
- Allocation scans the 256 level-0 entries in locality order, first forward from the start index and then backward.
- A bmap is considered usable if it has bitmap-granular availability or has a partial linear region for sub-16KB allocations.
- Class matching prefers empty or matching `(type << 8) | HAMMER2_PBUFRADIX` entries unless relaxed mode is active.
- On success, the target blockref receives `key | radix`, and data block allocations register dedup bits while the freemap leaf is still locked.
- On ENOSPC, `hammer2_freemap_iterate()` advances by 1GB leaves, wraps, and eventually switches to relaxed mode before returning real ENOSPC.

## Bitmap Allocation
- `hammer2_bmap_alloc()` allocates within a 4MB `hammer2_bmap_data`.
- Sub-16KB allocations can use the `linear` byte cursor inside an already allocated 16KB bitmap chunk.
- Larger allocations or block-aligned small allocations search the bitmap for clear two-bit groups; data blocks can use the low bits of the logical key to preserve sequential on-disk layout.
- It opportunistically calls `hammer2_io_newnz()` on a containing 64KB physical buffer if the whole physical buffer is newly unused, avoiding read-before-write.
- Availability and `allocator_free` are updated at bitmap granularity, not fine allocation granularity, because bulkfree cannot reconstruct sub-16KB allocation state.

## Freemap Initialization
- `hammer2_freemap_init()` marks unavailable portions of a new 1GB leaf as allocated:
  - Static allocations made by `newfs_hammer2`.
  - Reserved zone segment at the base of each applicable zone.
  - Trailing space past end-of-volume.
- Usable 4MB entries start with full availability; unavailable ones get all bitmap bits set, `avail = 0`, and `linear = HAMMER2_SEGSIZE`.

## Recovery Adjustment
- `hammer2_freemap_adjust()` is currently asserted for `HAMMER2_FREEMAP_DORECOVER`.
- It marks referenced blocks allocated during recovery when freemap updates may not have reached stable media before a crash.
- Static `newfs_hammer2` allocations are ignored because they predate dynamic freemap management.
- Missing leaves are created and initialized during recovery.
- The function sets bitmap bits to allocated, updates class if needed, reduces bmap availability and volume `allocator_free` at 16KB granularity, resets the linear allocator after modifications, sets `bigmask = -1`, and clears relaxed mode.
- Disabled code documents older may-free/real-free handling but notes availability accounting and state `10` semantics no longer match that implementation.

## Bulkfree Context
- The file ends with documentation for three-stage freemap validation:
  - Stage 1: allocated to possibly-free.
  - Stage 2: topology scan returns live blocks to allocated.
  - Stage 3: vetted possibly-free blocks become free.
- The implementation in this file does not include the bulkfree pass itself; it provides allocation and recovery primitives consumed by other HAMMER2 code.

## Important Constraints
- Reserved zones must never be dynamically allocated; successful normal allocation asserts the result is beyond `allocator_beg`, inside `total_size`, and past the zone reserved segment.
- Allocation hints are permissive. Clearing `bigmask` requires a full relaxed scan from the beginning; otherwise the allocator avoids making restrictive assumptions.
- Sub-16KB allocations cause deliberate internal accounting loss after unmount/reboot because only the 16KB bitmap state persists.
