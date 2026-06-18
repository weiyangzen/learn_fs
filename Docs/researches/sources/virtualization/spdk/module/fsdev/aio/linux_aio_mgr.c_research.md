# File Research: sources/virtualization/spdk/module/fsdev/aio/linux_aio_mgr.c

Implements the Linux libaio-backed AIO manager for fsdev AIO.

Key elements:
- Uses `io_context_t`, `iocb`, `io_submit`, `io_queue_run`, and `io_cancel`.
- Maintains a pool of `spdk_aio_mgr_io` objects and an in-flight list.
- Prepares `preadv` or `pwritev` requests and installs completion callback with `io_set_callback`.
- Completion removes AIO from in-flight, invokes fsdev callback, increments completion count, and returns object to pool.
- Poll returns busy when completions occurred.
- Delete asserts no in-flight operations and releases libaio context.

Dependencies:
- Linux libaio and SPDK queue/log/util APIs.
- Interface declared in `aio_mgr.h`.

Research notes:
- `io_submit()` success is treated as any nonzero result; libaio errors are negative, so callers should verify this handling against libaio conventions.
