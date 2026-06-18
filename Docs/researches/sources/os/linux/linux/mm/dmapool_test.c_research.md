# File Research: sources/os/linux/linux/mm/dmapool_test.c

## Purpose

A simple module-init timing and stress test for the DMA pool allocator in `dmapool.c`. It creates a synthetic device, creates pools with several size/alignment/boundary combinations, repeatedly allocates and frees many blocks, and prints elapsed time.

## Test Shape

- `NR_TESTS` is 100 iterations per parameter set.
- `pool_parms[]` covers block sizes 16, 64, 256, 1024, 4096, and a boundary-sensitive case `{ size = 68, align = 32, boundary = 4096 }`.
- `nr_blocks()` scales block count by page size and clamps it between 1024 and 8192.

## Main Functions

- `dmapool_test_alloc()` allocates `blocks` entries from the global `pool`, records virtual/DMA pairs, then frees all. On allocation failure it unwinds already allocated blocks.
- `dmapool_test_block()` allocates the pair array, creates one DMA pool, runs `NR_TESTS` allocate/free cycles, times with `ktime_get()`, logs microseconds, and destroys the pool.
- `dmapool_checks()` initializes and registers `test_dev`, sets a 64-bit coherent DMA mask, then runs all parameter tests.
- `dmapool_exit()` is empty; the test work runs during module init.

## Device Setup

The test uses a static `struct device test_dev` with:

- Name `dmapool-test`
- Empty release callback
- `set_dma_ops(&test_dev, NULL)`
- Static `dma_mask`
- `dma_set_mask_and_coherent(..., DMA_BIT_MASK(64))`

## Interfaces

Registered with:

- `module_init(dmapool_checks)`
- `module_exit(dmapool_exit)`

Metadata:

- `MODULE_DESCRIPTION("dma_pool timing test")`
- `MODULE_LICENSE("GPL")`

## Notes

This is not a KUnit-style assertion suite. It primarily checks allocator functionality under repeated create/alloc/free/destroy cycles and reports timing. Failures propagate as module init errors.
