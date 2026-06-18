# File Research: sources/os/linux/linux/fs/smb/smbdirect/socket.c

Owns SMB Direct socket creation, initial parameter validation, logging setup, cleanup scheduling, synchronous destruction, bind/shutdown/release, and a generic credit wait helper.

Key functions:
- `smbdirect_frwr_is_supported()` checks RDMA device FRWR capability by requiring memory management extensions and nonzero fast-registration page-list length.
- `smbdirect_socket_init_new()` initializes a new active socket and creates an RDMA CM ID.
- `smbdirect_socket_create_kern()` allocates and initializes a standalone socket with normal destroy kref.
- `smbdirect_socket_init_accepting()` initializes a socket around an accepted RDMA CM ID and sets device/context fields.
- `smbdirect_socket_create_accepting()` allocates such an accepting socket.
- `smbdirect_socket_set_initial_parameters()` validates flags, depth/resource values, optional IB/iWARP restrictions, and copies caller parameters.
- `smbdirect_socket_set_kernel_settings()` sets IB poll context and GFP masks for send/recv/RW allocations.
- `smbdirect_socket_set_logging()` installs frontend logging callbacks.
- `__smbdirect_socket_schedule_cleanup()` records the first error, disables non-cleanup work, recursively schedules cleanup for listener children, maps current status to the appropriate failure/disconnect status, wakes all wait queues, and queues cleanup work.
- `smbdirect_socket_cleanup_work()` performs asynchronous disconnect state progression and calls `rdma_disconnect()` when needed.
- `smbdirect_socket_destroy()` performs final teardown: disables work, drains QP, releases pending listener children, drains receive reassembly queue, destroys MR list, QP, RDMA CM ID, and memory pools, then marks destroyed.
- `smbdirect_socket_destroy_sync()` forces cleanup, waits for disconnected state if needed, and calls final destroy.
- `smbdirect_socket_bind()`, `smbdirect_socket_shutdown()`, and `smbdirect_socket_release()` provide exported lifecycle operations.
- `smbdirect_socket_wait_for_credits()` atomically consumes credits or sleeps until credits/status changes.

Important state and invariants:
- `first_error` is sticky and drives wakeups and later API failures.
- Cleanup wakes every wait queue: status, listener accept, send credits, pending sends, receive reassembly, RW credits, and MR readiness.
- There are two krefs:
  - `disconnect` represents frontend ownership and triggers synchronous disconnect/destroy at zero.
  - `destroy` represents backend memory lifetime and may be `REFCOUNT_MAX` for embedded sockets.
- `smbdirect_socket_release()` expects exactly one disconnect reference; violating that is treated as a bug.
- RDMA CM handler locking coordinates `rdma_disconnect()`, QP drain, and RDMA event callbacks.

Dependencies:
- Uses all other SMB Direct teardown helpers from `connection.c` and `mr.c`.
- Exports public socket setup/lifecycle symbols.

Maintenance notes:
- Cleanup and destroy paths are intentionally conservative and wake waiters repeatedly. New wait queues or async work items must be added to both wake/disable paths.
- `smbdirect_socket_wait_for_credits()` subtracts optimistically then adds back before sleeping; callers must restore any higher-level credits on later failures.
