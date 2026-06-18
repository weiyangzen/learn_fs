# File Research: sources/virtualization/qemu/block/blkio.c

This file implements QEMU block drivers backed by `libblkio`: `io_uring`, `nvme-io_uring`, `virtio-blk-vfio-pci`, `virtio-blk-vhost-user`, and `virtio-blk-vhost-vdpa`.

Key state:
- `BDRVBlkioState` stores the libblkio instance, queue, completion fd, a poll-side cached completion, locks, bounce-buffer pool/list/queue, memory-region properties, and whether memory regions may pin guest RAM.
- `blkio_lock` protects libblkio objects because libblkio is not thread-safe.
- `bounce_lock` protects bounce-buffer allocation state and must be acquired before `blkio_lock`.

I/O path:
- Completion fd handlers integrate libblkio queue completions into QEMU's AioContext.
- `blkio_completion_fd_poll()` can prefetch one completion into `poll_completion`; `blkio_completion_fd_read()` wakes the owning coroutine for cached and newly fetched completions.
- `blkio_co_preadv()`, `blkio_co_pwritev()`, `blkio_co_flush()`, `blkio_co_pdiscard()`, and `blkio_co_pwrite_zeroes()` submit libblkio requests, defer actual queue kicking through `defer_call()`, yield, and return completion status.
- If libblkio requires registered memory regions and the caller did not provide `BDRV_REQ_REGISTERED_BUF`, reads/writes use a bounce buffer.

Bounce-buffer management:
- The bounce pool is a libblkio memory region and is resized when no buffers are in flight and the current pool is too small.
- Allocations are tracked in address order and use a linear hole search.
- Waiting coroutines use `CoQueue` fairness: first wait joins the back, subsequent waits join the front to avoid losing place.

Memory registration:
- `blkio_mem_region_from_host()` validates alignment and optionally resolves RAMBlock fd/fd offset for drivers requiring fd-backed regions.
- `blkio_register_buf()` maps eligible memory regions unless unnecessary; `blkio_unregister_buf()` unmaps them.
- If a driver may pin memory, `blkio_open()` disables RAM discard via `ram_block_discard_disable(true)` until close.

Open/connect behavior:
- `blkio_io_uring_connect()` maps `filename` to libblkio `path` and sets `direct` when `BDRV_O_NOCACHE` is requested.
- `blkio_nvme_io_uring_connect()` requires `path` and requires direct cache mode.
- `blkio_virtio_blk_connect()` requires `path`, requires direct cache mode, tries fd passing when supported, falls back to path-based open for older/unsupported libblkio behavior, and handles fd cleanup on connect failure.
- `blkio_open()` creates the libblkio driver, sets read-only when needed, connects, queries memory-region properties, starts libblkio, initializes locks/queues, records supported flags, and installs the completion fd handler.

Limits and capabilities:
- `blkio_refresh_limits()` queries request alignment, optimal I/O size, max transfer, buffer alignment, optimal buffer alignment, and max segments from libblkio and validates them.
- Truncate does not grow or resize devices; it only accepts compatible no-op truncation.
- Block status and cache invalidation are noted as missing libblkio APIs.

Filesystem/block relevance:
- This is a high-performance virtual block transport integration layer.
- It bridges QEMU's coroutine/block API to external kernel/userspace backends and virtio transport mechanisms, including registered memory and zoned/zero/discard style constraints via block limits.

Potential pitfalls:
- Correctness depends on strict lock ordering: `bounce_lock` before `blkio_lock`.
- Registered buffers must be aligned to `mem_region_alignment`.
- Memory pinning has system-wide implications for RAM discard/virtio-mem.
- `blkio_close()` destroys `blkio_lock` before detaching AioContext handlers, which is the order implemented here and assumes no concurrent handler execution during close.
