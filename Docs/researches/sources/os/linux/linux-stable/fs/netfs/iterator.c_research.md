# File Research: sources/os/linux/linux-stable/fs/netfs/iterator.c

Provides iterator extraction and sizing helpers for netfs I/O.

Key behavior:
- `netfs_extract_user_iter()` pins/extracts user pages from ubuf/iovec iterators into a bvec iterator.
- Handles cleanup only for safe error cases; warns on impossible overrun/corruption situations.
- `netfs_limit_iter()` dispatches to iterator-specific limiters for bvec, kvec, xarray, and folio_queue iterators.
- Limiters cap a contiguous operation by both byte count and segment count.
- Xarray limiting walks folios under RCU and rejects value entries/hugetlb folios.
- Folio_queue limiting walks queue slots and chained queues.

Use:
- Read and write retry paths use this to renegotiate request sizes when a transport has max segment constraints.
