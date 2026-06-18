# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/virtio_blk.c

## Purpose

Implements a MINIX virtio-blk block driver with partition support, multithreaded request handling, virtqueue submission, flush support, geometry reporting, and graceful termination.

## Main Entry Points

- `main()`: parses environment, starts SEF, runs `blockdriver_mt_task()`, then cleans up.
- `sef_cb_init_fresh()`: probes the requested virtio block instance and announces the service.
- `virtio_blk_probe()`: sets up the virtio device, queue, request buffers, config, ready state, and IRQs.
- `virtio_blk_open()` / `virtio_blk_close()`: enforce read-only feature, parse partitions on first open, manage worker count and open count.
- `virtio_blk_transfer()`: maps caller buffers, constructs virtio-blk requests, submits them, sleeps until completion, and returns bytes/errors.
- `virtio_blk_flush()`: submits a flush request when supported.
- `virtio_blk_intr()` / `virtio_blk_device_intr()`: process used queue entries and wake the worker thread associated with each request.
- `virtio_blk_part()` / `virtio_blk_geometry()` / `virtio_blk_device()`: partition, geometry, and device-id callbacks.

## Control Flow And State

The driver negotiates a fixed feature table and keeps one global `blk_dev`. It allocates one request header and one status cell per worker thread in contiguous memory. First open initializes partition tables from the configured capacity and enables four workers; last close flushes, returns to one worker, and may terminate if SIGTERM was requested.

`virtio_blk_transfer()` validates sector-aligned iovecs, truncates at partition boundaries, maps grants to physical vectors with `sys_vumap()`, prepares a header with direction and sector, marks virtio descriptor write/read bits, appends the status byte, submits to queue 0 with the current thread id as callback data, and sleeps. The interrupt handler drains all completed queue entries and wakes the stored thread ids.

## Dependencies

Depends on MINIX blockdriver_mt, virtio library APIs, safe virtual-to-physical grant mapping, disk ioctls, partition parsing, and definitions from `virtio_blk.h`.

## Risks

Correctness depends on per-thread request/status storage matching the worker id returned by `blockdriver_mt_get_tid()`. Queue completion must wake exactly the submitted thread. The driver assumes 512-byte logical sectors even if the host advertises another block size. Partial partition truncation adjusts vectors in place before mapping. Flush is optional and returns `EOPNOTSUPP` if unsupported; close ignores that return.
