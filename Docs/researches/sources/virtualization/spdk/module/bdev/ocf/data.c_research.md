# File Research: sources/virtualization/spdk/module/bdev/ocf/data.c

This file implements the lightweight data container used to pass SPDK bdev I/O buffers into OCF. `vbdev_ocf_data_alloc()` allocates a `bdev_ocf_data` and optional owned iovec array with OCF environment allocation. `vbdev_ocf_data_free()` frees the owned iovec array only when `iovalloc` is nonzero.

`vbdev_ocf_iovs_add()` appends a base/length pair into an allocated iovec array and logs an error if capacity is exceeded, though it does not grow the array. `vbdev_ocf_data_from_spdk_io()` maps an existing `spdk_bdev_io` driver context into an OCF data object by borrowing the bdev I/O iovs, setting iov count, and computing data size from block count and block length.

Supported SPDK I/O types for mapping are read, write, flush, and unmap. Read/write require iovs; flush and unmap do not. Unsupported I/O types log an error and return null. The main invariant is ownership: data objects created from SPDK I/O borrow iovs and must not free them as owned arrays.
