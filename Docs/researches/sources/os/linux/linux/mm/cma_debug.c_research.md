# File Research: sources/os/linux/linux/mm/cma_debug.c

## Purpose
Provides a debugfs interface for inspecting and manually exercising CMA areas.

## Main Interfaces
- Debugfs read attributes: `count`, `order_per_bit`, `used`, `maxchunk`, per-range `base_pfn`, and per-range `bitmap`.
- Debugfs write attributes: `alloc` allocates pages from a CMA area; `free` releases pages previously allocated through this debug interface.
- Init: `cma_debugfs_init()` creates `/sys/kernel/debug/cma` entries for activated CMA areas.

## Control Flow
Manual allocation creates a `cma_mem` tracking entry, allocates pages with `cma_alloc()`, and stores the allocation on a per-CMA debug list. Manual free pops tracked entries and releases full allocations, or partial allocations only when `order_per_bit == 0`; otherwise it keeps the remainder tracked and logs that partial block release is unsupported.

## State And Synchronization
Uses `cma->lock` to read allocation bitmap-derived state and `cma->mem_head_lock` to protect the debug allocation tracking list.

## Integration Points
Calls CMA core allocation/release functions and exposes raw CMA bitmap data through debugfs. Creates backward-compatible `base_pfn` and `bitmap` symlinks to range `0`.

## Risks And Review Focus
- This is a privileged debug interface that can perturb allocator state.
- Partial free behavior differs when bitmap granularity represents more than one page.
- Debugfs bitmap exposure depends on `unsigned long` bitmap storage cast into a `u32` array view.
