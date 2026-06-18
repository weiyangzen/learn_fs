# File Research: sources/virtualization/spdk/lib/nbd/nbd.c

Core SPDK NBD implementation. It exports an SPDK bdev through a Linux `/dev/nbdX` device using a nonblocking socketpair and the kernel NBD ioctls.

Key data structures:
- `nbd_io` tracks one NBD request through receive header, receive write payload, transmit response, and transmit read payload states.
- `spdk_nbd_disk` holds bdev descriptor/channel, NBD device fd, socketpair fds, poller/interrupt state, retry state, active IO queues, lifecycle flags, and list linkage.
- Global disk list `g_spdk_nbd.disk_head` records active exports.

Lifecycle:
- `spdk_nbd_init` initializes the global disk list.
- `spdk_nbd_start` opens a bdev, gets an IO channel, creates a nonblocking socketpair, registers the disk, opens the NBD device, then calls `NBD_SET_SOCK`.
- `nbd_start_continue` configures block size, block count, timeout, flush/trim feature flags, starts a detached kernel thread that blocks in `NBD_DO_IT`, and registers SPDK poller/interrupt handling.
- `spdk_nbd_stop` marks closing, drains or fails pending IO, unregisters pollers/interrupts, closes fds, clears kernel queues/sockets if still registered, releases bdev resources, unregisters disk, and frees state.
- `spdk_nbd_fini` stops all disks asynchronously and invokes the fini callback when the global list is empty.

IO path:
- `nbd_io_recv_internal` reads NBD request headers and write payloads from the socket, validates magic, handles `NBD_CMD_DISC`, allocates DMA-aligned payload buffers, and queues requests.
- `nbd_submit_bdev_io` maps NBD READ/WRITE/FLUSH/TRIM to SPDK bdev read/write/flush/unmap.
- `nbd_io_done` fills the NBD reply, moves IO from processing to executed, and enables writable interrupt notification when needed.
- `nbd_io_xmit_internal` writes replies and read payloads back to the kernel NBD socket.
- `nbd_poll` drives transmit, receive, and bdev submission until idle or error.

Dependencies:
- Linux `<linux/nbd.h>`, SPDK bdev/env/thread/log/endian/util/queue APIs, socketpair/ioctl/open/close/read/write.
- Requires Linux NBD kernel support and `/dev/nbdX` devices.

Research notes:
- The design keeps kernel blocking work in detached pthreads while bdev IO stays on SPDK threads.
- Stop logic has busy-wait retry pollers for both startup `EBUSY` and shutdown `NBD_DO_IT` return.
- Hot-remove marks the disk closing and fails queued requests.
- Scope relevance is high: this bridges SPDK userspace block devices into the kernel block stack for virtualization and storage integration.
