# File Research: sources/os/linux/linux/mm/cma.h

## Purpose
Defines internal CMA data structures, flags, global declarations, bitmap helpers, and sysfs accounting hooks shared by CMA core, debugfs, and sysfs files.

## Main Contents
- `cma_memrange` describes each CMA physical range with base PFN, page count, early-reservation PFN before activation or bitmap after activation, and optional debugfs bitmap wrapper.
- `cma` describes an allocator area: total/available pages, bitmap granularity, locks, optional debugfs allocation tracking, name, range array, optional sysfs counters/kobject, flags, and NUMA node.
- `cma_kobject` binds a sysfs kobject back to a `struct cma`.
- `CMA_MAX_RANGES` limits multi-range CMA to 8 ranges.
- `cma_bitmap_maxno()` computes the bitmap size in allocation units.

## Integration Points
Included by `cma.c`, `cma_debug.c`, and `cma_sysfs.c`. Exposes `cma_areas` and `cma_area_count` to debug/visibility code and hides sysfs counter calls behind config stubs.

## Risks And Review Focus
- The `early_pfn`/`bitmap` union changes meaning after activation.
- `available_count`, bitmap bits, and sysfs counters must remain consistent with allocation/release code.
- Flag additions must preserve the one-bit state checks used by activation and validation.
