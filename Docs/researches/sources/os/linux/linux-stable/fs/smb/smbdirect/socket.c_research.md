# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.c

## Purpose
Socket object lifecycle, public construction/configuration APIs, central cleanup/disconnect/destroy handling, bind/shutdown/release, and generic credit wait helper.

## Creation and Configuration
- `smbdirect_frwr_is_supported()` requires `IB_DEVICE_MEM_MGT_EXTENSIONS` and nonzero `max_fast_reg_page_list_len`.
- `smbdirect_socket_init_new()` initializes a socket, creates an RDMA CM ID, enforces address-family-only behavior, and installs cleanup work.
- `smbdirect_socket_create_kern()` allocates a standalone kernel socket and initializes destroy refcount.
- `smbdirect_socket_init_accepting()` initializes a socket around an accepted RDMA CM ID, sets context/handler, and caches `ib.dev`.
- `smbdirect_socket_create_accepting()` allocates a standalone accepting socket.
- `smbdirect_socket_set_initial_parameters()` is only valid in `CREATED`, validates flags/depth/resource limits, optionally restricts RDMA node type, and copies parameters.
- `smbdirect_socket_set_kernel_settings()` is only valid in `CREATED` and sets CQ polling context plus GFP masks.
- `smbdirect_socket_set_logging()` installs upper-layer logging callbacks.

## Central Cleanup
- `__smbdirect_socket_schedule_cleanup()`:
  - records first error once
  - disables connect/refill/immediate/idle work without waiting
  - clears keepalive state
  - recursively schedules cleanup for listener pending/ready accepted sockets
  - maps current status to failed/disconnected/error state
  - applies optional forced status
  - wakes all waitqueues
  - queues `disconnect_work`
- `smbdirect_socket_cleanup_work()`:
  - ensures first error exists
  - disables work
  - propagates cleanup to accepted sockets for listeners
  - for connected/negotiating/error sockets, transitions to disconnecting and calls `rdma_disconnect()` under RDMA handler lock
  - for pre-established states, moves directly to disconnected
  - wakes all waiters

## Destruction
- `smbdirect_socket_destroy()` expects disconnected state, disables all work synchronously, locks RDMA handler, drains QP, releases listener child sockets, drains receive reassembly buffers, destroys MR list, QP, RDMA CM ID, and mempools, then marks `DESTROYED`.
- `smbdirect_socket_destroy_sync()` disables future disconnect work, schedules shutdown cleanup if needed, waits for disconnected state, then calls destroy.
- `smbdirect_socket_release()` drops the frontend disconnect reference and backend destroy reference; standalone sockets are freed when destroy ref reaches zero.

## Other APIs
- `smbdirect_socket_bind()` wraps `rdma_bind_addr()` for created sockets.
- `smbdirect_socket_shutdown()` schedules cleanup with `-ESHUTDOWN`.
- `smbdirect_socket_wait_for_credits()` atomically reserves credits or waits interruptibly until credits are available or socket status changes.

## Concurrency Model
- Waitqueues for status, listener accept, send credits, pending sends, receive reassembly, RW credits, and MR readiness are all woken on cleanup.
- RDMA handler lock coordinates disconnect/destroy ordering around `rdma_disconnect()`, `ib_drain_qp()`, and CM callbacks.
