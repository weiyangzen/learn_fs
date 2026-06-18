# File Research: sources/virtualization/spdk/module/bdev/uring/bdev_uring.c

## Purpose
Implements a file/block-device-backed SPDK bdev using Linux `io_uring`.

## State
- `struct bdev_uring`: SPDK bdev, filename, fd, optional zoned metadata, and hot-remove flag.
- `struct bdev_uring_group_channel`: per-module channel with `io_uring`, pending/in-flight counts, poller, and detached flag.
- `struct bdev_uring_io_channel`: per-bdev channel referencing the group channel.
- `struct bdev_uring_task`: per-I/O context with expected length and channel pointer.

## Lifecycle
`create_uring_bdev()` opens the file/device, detects or validates block size, checks zoned support when enabled, validates size alignment, registers bdev and I/O device, and inserts it into `g_uring_bdev_head`.

Destruction unregisters the bdev, closes fd, unregisters the I/O device, and frees memory. Module init registers a shared module I/O device that creates per-thread `io_uring` queues.

## I/O Path
Read/write requests acquire aligned bdev buffers, enqueue `io_uring_prep_readv/writev` SQEs, and are submitted by `bdev_uring_group_poll()`. The same poller reaps CQEs and completes bdev I/O.

Completion checks `cqe->res` against expected byte count. `-EAGAIN`/`-EWOULDBLOCK` map to `NOMEM`; other short/error completions may trigger detach detection via `spdk_fd_get_size(fd) == 0`.

## Zoned Support
Under `SPDK_CONFIG_URING_ZNS`, the module detects host-aware/host-managed block devices from sysfs, reads zone count/size/open/active limits, implements zone management via `BLKRESETZONE`, `BLKOPENZONE`, `BLKCLOSEZONE`, `BLKFINISHZONE`, and implements zone reports via `BLKREPORTZONE`.

## Control Plane
`bdev_uring_rescan()` reopens the bdev by name, checks fd size, hot-removes zero-sized detached devices, and notifies block-count changes on resize.

## Invariants And Risks
- Queue depth is fixed at 512 and CQE reap is bounded by current in-flight count.
- `io_pending` is converted to `io_inflight` after `io_uring_submit()`.
- Device detach detection is heuristic and depends on fd size becoming zero.
- Zoned support is compile-time conditional.
