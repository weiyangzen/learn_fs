# File Research: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.c

Implements the non-Linux/portable POSIX AIO manager used by fsdev AIO.

Key elements:
- Uses pools of `spdk_aio_mgr_io` and `spdk_aio_mgr_req`.
- Splits vector I/O into POSIX `aiocb` requests, with up to `REQS_PER_AIO` request objects per AIO.
- Submits with `aio_read()` or `aio_write()`.
- Supports cancellation through `aio_cancel()`.
- Polls in-flight requests with `aio_error()` and completes with `aio_return()`.
- Returns completed request and AIO objects to internal pools.
- Deletes only when no in-flight AIOs remain.

Dependencies:
- POSIX AIO, SPDK queue, util, and logging APIs.
- Interface declared in `aio_mgr.h`.

Research notes:
- Callback error values are positive errno-style values, later passed through fsdev completion.
