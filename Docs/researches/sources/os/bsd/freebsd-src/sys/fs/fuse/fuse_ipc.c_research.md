# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.c

This file implements the kernel-side FUSE IPC machinery: reusable request tickets, request/reply queues, dispatchers, daemon-response auditing, interrupt delivery, and FUSE session lifecycle support.

Key responsibilities:
- Manages dynamic FUSE message buffers through `struct fuse_iov`.
  - `fiov_init`, `fiov_adjust`, `fiov_refresh`, and `fiov_teardown` allocate, resize, clear, and shrink request/response buffers.
  - Sysctls `iov_permanent_bufsize` and `iov_credit` control when oversized buffers are tolerated or reallocated smaller.
- Manages `struct fuse_ticket` objects through a UMA zone.
  - Constructor binds a ticket to `struct fuse_data`, resets state, assigns a unique id, and increments `ticket_count`.
  - Init/fini create and destroy message/answer buffers and the answer mutex.
  - `fticket_refresh` clears buffers; `fticket_reset` reuses existing buffers without clearing payload.
  - `fuse_ticket_drop` releases the refcount and returns the ticket to UMA when the last reference drops.
- Implements waiting for daemon answers in `fticket_wait_answer`.
  - Blocks signals unless the mount supports interruptible operations and `FSESS_INTR`.
  - Sleeps on the ticket answer mutex for `daemon_timeout`.
  - Converts timeout to `ETIMEDOUT`.
  - On interruption, sends `FUSE_INTERRUPT` when possible and waits for protocol-level interruption.
  - Returns `ENOTCONN` when the session is dead.
- Implements `FUSE_INTERRUPT`.
  - `fuse_interrupt_send` either removes an unsent original request and completes it locally, or sends an urgent `FUSE_INTERRUPT` request for an already delivered operation.
  - `fuse_interrupt_callback` handles interrupt replies, caches `ENOSYS`, resends on `EAGAIN` when the original still exists, and rejects illegal replies.
- Implements session allocation and death.
  - `fdata_alloc` initializes request and answer queues, kqueue/select state, daemon credentials, timeout, and initial refcount.
  - `fdata_set_dead` marks `FSESS_DEAD`, wakes request waiters and device readers, and prevents new useful traffic.
  - `fdata_trydestroy` releases credentials, locks, kqueue state, and memory when the reference count reaches zero.
- Implements request queue insertion.
  - `fuse_insert_callback` installs an answer handler and enqueues on the answer queue.
  - `fuse_insert_message` marks a ticket dirty, enqueues it on the daemon message queue, wakes `/dev/fuse` readers, and notifies kqueue/select waiters.
  - Urgent messages are inserted at the queue head.
- Implements daemon response handling helpers.
  - `fticket_pull` validates expected body length using `fuse_body_audit` and copies response body into the ticket response buffer.
  - `fuse_body_audit` verifies reply sizes per opcode, including compatibility sizes for older protocol versions and variable lengths for xattr/readdir/read/ioctl cases.
  - `fuse_standard_handler` pulls response data, marks the ticket answered, stores any IPC-level error, and wakes the waiter.
- Implements `fuse_dispatcher` helpers.
  - `fdisp_make`, `fdisp_make_vp`, and internal pid-based variants allocate or refresh a ticket, allocate the input buffer, and fill `fuse_in_header`.
  - `fdisp_refresh_vp` reuses a dispatcher without zeroing payload, used by retry paths.
  - `fdisp_wait_answ` installs the standard handler, queues the request, waits, maps communication errors to `EIO`/`ENOTCONN`, preserves protocol errors in `answ_stat`, and exposes successful response pointer/size.
- Provides initialization/destruction:
  - `fuse_ipc_init` creates the ticket UMA zone and counter.
  - `fuse_ipc_destroy` frees both.
- Provides `fuse_warn`, a once-per-session protocol violation warning helper.

Integration points:
- The `/dev/fuse` device layer, outside this file, pops message-queue tickets and writes replies into answer-queue tickets.
- All FUSE operation helpers in `fuse_internal.c`, `fuse_io.c`, `fuse_vfsops.c`, and vnode ops use `fuse_dispatcher`.
- Session flags and mount state are declared in `fuse_ipc.h`.

Notable risks and research hooks:
- `fuse_body_audit` is a central protocol hardening point; missing new opcodes or incorrect reply lengths panic or return `EINVAL`.
- Interrupt handling depends on FUSE daemon semantics and may wait for original completion if interrupts are unsupported.
- `fticket_reset` notes unique ids may truncate on LP32 architectures.
- `fuse_insert_message` panics if a dirty ticket is reused without refresh.
- Timeout is per mount via `daemon_timeout`; a timed-out operation is marked answered from the kernel perspective.
