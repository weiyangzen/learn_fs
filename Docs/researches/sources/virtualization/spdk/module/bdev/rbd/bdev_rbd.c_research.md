# File Research: sources/virtualization/spdk/module/bdev/rbd/bdev_rbd.c

## Purpose
Implements the SPDK bdev module backed by Ceph RBD images via `librados` and `librbd`.

## Main State
- `struct bdev_rbd`: bdev wrapper holding RBD image, pool/user/config, cluster reference, IO context, reset state, resize watch handle, and read-only flag.
- `struct bdev_rbd_cluster`: named shared Rados cluster registration with config, key file, optional CPU mask, and refcount.
- `struct bdev_rbd_pool_ctx`: shared pool IO context keyed by cluster pointer and pool name.
- `struct bdev_rbd_io`: per-I/O context storing submit thread, status, RBD completion, and expected read length.

## Lifecycle
`bdev_rbd_create()` validates pool/image/block size, duplicates config strings, initializes a private or named shared Rados cluster, opens the image, reads image stats, registers an SPDK I/O device, and registers the bdev.

Cluster creation and image open are run via `spdk_call_unaffinitized()` to avoid Rados work running on SPDK reactor threads. Named clusters are protected by `g_map_bdev_rbd_cluster_mutex`; pool contexts are app-thread-owned and refcounted.

Destruction is asynchronous. `bdev_rbd_destruct()` sends cleanup to the app thread, unregisters the I/O device, then returns to the original destruct thread before calling `spdk_bdev_destruct_done()`.

## I/O Path
Supported operations:
- read, write, unmap/discard, flush, write zeroes
- reset
- compare-and-write when `LIBRBD_SUPPORTS_COMPARE_AND_WRITE_IOVEC` is available

Reads acquire a bdev buffer first. `bdev_rbd_start_aio()` creates a librbd completion and dispatches `rbd_aio_read/readv`, `write/writev`, `discard`, `flush`, `write_zeroes`, or compare-and-write. Completion status is translated back to SPDK bdev status and marshaled to the original submit thread if librbd completes elsewhere.

Reset is a workaround: librbd cannot cancel outstanding AIO, so reset polls current queue depth until in-flight I/O drains.

## Control Plane
Exports creation, deletion, resize, cluster register/unregister, and cluster info helpers used by the RPC file. `bdev_rbd_resize()` opens the bdev, verifies it is RBD, prevents shrinking, calls `rbd_resize()`, then notifies block-count change.

RBD image update watch calls into SPDK app thread and updates bdev block count on image size changes.

## Dependencies
Uses Ceph `librados`/`librbd`, SPDK bdev module APIs, JSON, thread messaging, pollers, cpuset handling, and bdev queue-depth queries.

## Invariants And Risks
- Shared cluster references must be returned through `bdev_rbd_put_cluster()`.
- Pool context mutations assert app-thread context.
- Reset does not abort librbd I/O; it waits for outstanding I/O to complete.
- `bdev_rbd_delete()` assumes a callback is supplied when unregister by name fails.
- Read-only RBD bdevs disable writes, write zeroes, and compare-and-write.
