# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_priority.h

Defines queue priority classes for ZIO scheduling.

Key elements:
- `zio_priority_t` includes sync read, sync write/ZIL, async read/prefetch, async write/spa_sync, scrub/resilver, vdev removal, initializing, trim, queueable sentinel, and now/non-queued I/O.
- Comment requires `ZIO_PRIORITY_NUM_QUEUEABLE` to match the public `ZIO_PRIORITY_N_QUEUEABLE` value in `uts/common/sys/fs/zfs.h`.

Main dependencies and interactions:
- Included by `zio.h`.
- Consumed by vdev queueing and ZIO creation APIs.

Implementation notes:
- Ordering is a scheduler contract. Changes must be mirrored in public ZFS definitions.
