# File Research: sources/os/linux/linux/fs/netfs/iterator.c

Provides iterator extraction and span-limiting helpers for netfs I/O.

Important exported APIs:
- `netfs_extract_user_iter()`: pins/extracts pages from user iterators into a bvec iterator.
- `netfs_limit_iter()`: returns a byte span limited by max size and max segment count.

Supported iterator types in `netfs_limit_iter()`:
- `ITER_BVEC`.
- `ITER_KVEC`.
- `ITER_XARRAY`.
- `ITER_FOLIOQ`.

Important behavior:
- `netfs_extract_user_iter()` only accepts ubuf/iovec iterators, allocates bvec storage, places temporary page pointers at the end of that allocation, and advances the original iterator.
- Error cleanup only unpins pages when it is safe to trust the partial result.
- Xarray limiting scans folios under RCU and rejects value entries or hugetlb folios.
- Folio-queue limiting walks across linked `folio_queue` structures.

Dependencies:
- Generic `iov_iter` extraction APIs.
- Folio queue iterator support used by rolling buffer write/read machinery.
