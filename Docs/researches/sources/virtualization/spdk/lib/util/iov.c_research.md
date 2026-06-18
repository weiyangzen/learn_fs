# File Research: sources/virtualization/spdk/lib/util/iov.c

This file provides generic iovec memory operations and iterators.

`spdk_iov_memset()` fills all iovec buffers. `spdk_ioviter_first()` and `spdk_ioviter_firstv()` initialize two-way or N-way iterators. `spdk_ioviter_next()` and `spdk_ioviter_nextv()` return the next aligned span length across all tracked iovec lists, advancing each list by the minimum remaining segment size. Iteration stops when any stream is exhausted.

`spdk_iovcpy()` and `spdk_iovmove()` copy or memmove between source and destination iovec arrays using the two-way iterator, returning the total transferred bytes.

`spdk_iov_xfer_init()` initializes a one-way transfer cursor. `spdk_iov_xfer_from_buf()` copies from a flat buffer into iovecs, while `spdk_iov_xfer_to_buf()` copies from iovecs into a flat buffer. `spdk_copy_iovs_to_buf()` and `spdk_copy_buf_to_iovs()` are convenience wrappers.

The iterators assume nonempty iovec arrays when initialized and do not perform deep validation of null bases or invalid counts. The transfer cursor preserves position across calls, making it useful for incremental protocol marshalling.
