# File Research: sources/os/linux/linux/mm/cma.c

## Purpose
Implements the Contiguous Memory Allocator core: early reservation of CMA regions, activation into pageblock-managed areas, bitmap-based allocation, contiguous-page migration/freezing, release, multi-range CMA support, and early sub-reservation.

## Main Interfaces
- Metadata access: `cma_get_base()`, `cma_get_size()`, `cma_get_name()`, `cma_for_each_area()`, `cma_intersects()`.
- Reservation/setup: `cma_init_reserved_mem()`, `cma_declare_contiguous_nid()`, `cma_declare_contiguous_multi()`, `cma_reserve_pages_on_error()`.
- Allocation/release: `cma_alloc()`, `cma_alloc_frozen()`, `cma_alloc_frozen_compound()`, `cma_release()`, `cma_release_frozen()`.
- Early reservation: `cma_reserve_early()`.

## Control Flow
Early declaration reserves fixed or dynamically chosen memblock ranges, validates alignment and size against pageblock and `order_per_bit`, creates a CMA descriptor, and records one or more ranges. Activation later allocates per-range bitmaps, validates that each range stays within a single zone, marks already early-reserved portions as used, initializes reserved pageblocks as CMA, initializes locks/debug lists, and marks the area activated.

Allocation searches each range bitmap for an aligned free span, marks it allocated under `cma->lock`, then calls `alloc_contig_frozen_range()` under `alloc_mutex` to isolate/migrate pages. On busy failure it clears the bitmap and retries; on success it resets KASAN tags and updates VM events/sysfs counters. Normal `cma_alloc()` also makes pages refcounted. Release validates the page range belongs to a CMA range, drops page refs for normal release, frees the frozen contiguous range, clears bitmap bits, and updates counters/tracepoints.

## State And Synchronization
Global state is `cma_areas[]` plus `cma_area_count`. Each CMA area has a spinlock for bitmap and `available_count`, a mutex serializing contiguous allocation, per-range bitmaps, flags recording activation/zone validation/error behavior, and optional debugfs/sysfs accounting state.

## Integration Points
Uses memblock for boot reservations, pageblock migration-type initialization, contiguous allocation/freeing, memory isolation/migration, KASAN tag reset, kmemleak physical ignores, VM event counters, tracepoints, and optional CMA debugfs/sysfs accounting.

## Notable Behaviors
- Multi-range declaration first tries a single region, then selects the largest suitable above-4G free ranges and reserves them bottom-up.
- Dynamic allocation avoids the first 4GB when possible on 64-bit systems to preserve constrained DMA/DMA32 zones.
- CMA ranges crossing zones are rejected because `alloc_contig_range()` requires a single-zone PFN range.
- `cma_reserve_early()` can reserve aligned chunks before activation without locking or later unreserve support.

## Risks And Review Focus
- Bitmap accounting and contiguous allocation rollback must remain paired on every failure path.
- Zone validation and highmem/lowmem boundary checks protect allocator assumptions.
- Multi-range failure cleanup must free only successfully reserved memblock ranges.
- Early reservations are caller-managed if CMA activation later fails.
