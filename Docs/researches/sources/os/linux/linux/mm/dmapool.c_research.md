# File Research: sources/os/linux/linux/mm/dmapool.c

## Purpose

Implements the Linux generic DMA pool allocator for small coherent DMA objects. A `struct dma_pool` owns pages allocated via `dma_alloc_coherent()`, subdivides them into fixed-size blocks, and serves those blocks to drivers that need small, aligned, coherent DMA buffers.

## Core Data Structures

- `struct dma_pool`: pool metadata, including `page_list`, `next_block` free list, size/alignment-derived geometry, counters, device pointer, NUMA node, sysfs list node, and pool name.
- `struct dma_page`: per-coherent-allocation page header with virtual address and DMA address.
- `struct dma_block`: free-list node stored inside free blocks; records next block and DMA address.

## Main Behavior

- `dma_pool_create_node()` validates device, size, alignment, and boundary constraints, normalizes block size, chooses allocation size, allocates the pool, and registers it under `dev->dma_pools`.
- A per-device read-only sysfs attribute `pools` is created when the first pool is registered and removed when the last pool is destroyed.
- `pool_initialise_page()` splits a coherent allocation into valid blocks, honoring the configured boundary by skipping offsets that would cross it.
- `dma_pool_alloc()` pops a free block under `pool->lock`; if no block exists, it allocates a new coherent page outside the spinlock, initializes it, and retries.
- `dma_pool_free()` validates/debug-poisons the block, pushes it onto the free list, and decrements active allocation count.
- `dma_pool_destroy()` unregisters the pool, warns if still busy, frees all backing coherent pages only when no active blocks remain, and frees metadata.
- `dmam_pool_create()` / `dmam_pool_destroy()` wrap pool lifetime in devres-managed resources.

## Debug / Hardening Paths

When `DMAPOOL_DEBUG` is enabled through `CONFIG_SLUB_DEBUG_ON`:

- Freed blocks are filled with `POOL_POISON_FREED`.
- Allocation checks verify the freed poison pattern after the embedded `struct dma_block`.
- Free validates the DMA address belongs to a pool page and detects double free by scanning the free list.
- Allocated blocks can be filled with `POOL_POISON_ALLOCATED` unless init-on-alloc is requested.

Without debug, free still honors `init_on_free` by zeroing the block.

## Locking and Concurrency

- `pool->lock` protects the free list and allocation counters.
- `pools_lock` protects the per-device `dma_pools` list.
- `pools_reg_lock` serializes sysfs file creation/removal races across pool create/destroy.
- Page allocation is done outside `pool->lock` because coherent DMA allocation can sleep.

## Dependencies and Interfaces

Exports:

- `dma_pool_create_node`
- `dma_pool_destroy`
- `dma_pool_alloc`
- `dma_pool_free`
- `dmam_pool_create`
- `dmam_pool_destroy`

Consumes core DMA APIs, devres, sysfs device attributes, poisoning helpers, GFP init policy helpers, spinlocks, and device pool list infrastructure.

## Important Invariants

- Alignment must be a power of two; zero alignment becomes one.
- Block size is at least `sizeof(struct dma_block)` and aligned up to requested alignment.
- Boundary is either zero, a power of two, and at least block size; internally capped to allocation size.
- Free-list nodes are embedded in unused DMA blocks.
- Used blocks are not individually tracked; correctness depends on active count and debug validation.
