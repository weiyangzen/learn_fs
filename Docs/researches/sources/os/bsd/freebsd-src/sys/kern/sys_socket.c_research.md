# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_socket.c

## Purpose
Defines socket file descriptor operations and generic socket AIO support, connecting FreeBSD sockets to the generic `struct file` layer, ioctl/poll/kqueue/stat/kinfo interfaces, close behavior, and asynchronous read/write execution.

## Main Elements
- `socketops`: `fileops` table for socket read, write, ioctl, poll, kqueue, stat, close, fdclose, chmod, kinfo, AIO queueing, comparison, and descriptor passing.
- `soo_read()` / `soo_write()`: perform MAC checks and call `soreceive()` / `sousrsend()`.
- `soo_ioctl()`: handles generic socket descriptor ioctls such as nonblocking, async, byte counts, ownership, process group, at-mark, and dispatches interface, routing, or protocol-specific ioctls.
- `soo_poll()` and `soo_kqfilter()`: delegate readiness and kqueue behavior to protocol switch methods.
- `soo_stat()`: synthesizes socket stat metadata, readability/writability mode bits, receive size, uid/gid, and protocol-specific `pr_sense`.
- `soo_close()` / `soo_fdclose()` / `soo_chmod()`: close sockets, notify protocols of fd close, and delegate chmod where supported.
- `soo_fill_kinfo()`: fills `kinfo_file` socket details for protocol/domain/type, PCB pointers, queues, local/peer socket addresses, and UNIX-domain peer pointers.
- Socket AIO subsystem:
  - `soaio_init()`, `soaio_enqueue()`, `soaio_kproc_create()`, `soaio_kproc_loop()` manage socket AIO worker kernel processes and job queues.
  - `soaio_process_job()` and `soaio_process_sb()` run queued read/write AIO jobs against socket buffers.
  - `sowakeup_aio()`, `soo_aio_cancel()`, `soo_aio_queue()`, `soaio_queue_generic()` integrate readiness wakeups, cancellation, and generic protocol AIO queueing.

## Dependencies And Integration
Uses socket/protocol switch APIs, sockbuf locking, virtual network context switching, MAC socket hooks, network routing/interface ioctls, AIO kernel job infrastructure, taskqueues, kprocs, file descriptor metadata, UNIX and INET PCB state, and select/kqueue readiness support.

## Risk Notes
AIO execution temporarily switches vmspace and credentials to match the submitting job, so credential restoration and cancellation correctness matter. The ioctl path mixes unlocked reads for some socket state with locked sockbuf access elsewhere. Protocol delegation means correctness depends on each protocol’s `pr_*` methods honoring locking and vnet expectations.
