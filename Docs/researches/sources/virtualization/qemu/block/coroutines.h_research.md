# File Research: sources/virtualization/qemu/block/coroutines.h

Internal block-layer coroutine declarations. It groups thread-safe I/O API functions and mixed I/O/global-state wrappers used by generated block code and block drivers.

Declared coroutine/read-lock functions include `bdrv_co_check()`, `bdrv_co_invalidate_cache()`, `bdrv_co_common_block_status_above()`, VMState read/write helpers, and NBD connection establishment. Mixed wrapper declarations expose `bdrv_common_block_status_above()` and `nbd_do_establish_connection()` with generated coroutine wrapper annotations.
