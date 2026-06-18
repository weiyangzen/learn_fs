# File Research: sources/os/bsd/openbsd-src/sys/kern/dma_alloc.c

Small DMA-safe allocation pool implementation.

Key behavior:
- Creates DMA pools for object sizes from 2^4 through 2^16.
- `dma_alloc_init()` initializes pools, names them `dma<size>`, and applies `kp_dma_contig` constraints.
- `dma_alloc_index()` selects the smallest bucket fitting a requested size.
- `dma_alloc()` returns `pool_get()` from the selected bucket.
- `dma_free()` returns memory to the matching pool.

Filesystem/OS relevance:
- Provides constrained contiguous memory allocation for DMA-capable kernel subsystems, including storage/device drivers.
