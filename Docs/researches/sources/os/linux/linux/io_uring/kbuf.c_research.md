# File Research: sources/os/linux/linux/io_uring/kbuf.c

Provided-buffer implementation for io_uring. It supports legacy kernel-owned buffer lists and mmap/user-backed provided buffer rings, including incremental consumption, bundle selection, registration, unregistration, and status reporting.

Key flows:
- Selection: `io_buffer_select()` chooses legacy or ring buffers by buffer group. Ring mode reads tail with acquire ordering, marks selected buffer state, and may commit immediately depending on context/pollability.
- Multi-buffer selection: `io_buffers_select()` and `io_buffers_peek()` build iovec arrays for bundled send/recv, expanding cached vectors up to `PEEK_MAX_IMPORT`.
- Commit/recycle: `io_kbuf_commit()` advances ring heads or incrementally consumes buffer length/address; `__io_put_kbufs()` returns CQE buffer flags and `IORING_CQE_F_BUF_MORE` when partial/incremental buffers remain.
- Legacy management: `io_provide_buffers_prep()`, `io_remove_buffers_prep()`, and `io_manage_buffers_legacy()` validate SQEs and add/remove `struct io_buffer` nodes.
- Ring registration: `io_register_pbuf_ring()` validates `io_uring_buf_reg`, creates a mapped region via `io_create_region()`, sets mask/flags/min-left, handles SHM aliasing constraints, and publishes the group in `ctx->io_bl_xa`.
- Ring unregistration/status: unregister erases the xarray entry under `mmap_lock`; status returns the kernel head.

Important details:
- Buffer group IDs map through `ctx->io_bl_xa`.
- `ctx->mmap_lock` protects visibility to mmap lookups.
- Legacy selected buffers are owned by requests until recycled or dropped.
- Ring buffers use `REQ_F_BUFFERS_COMMIT`, `REQ_F_BUFFER_RING`, and `REQ_F_BL_NO_RECYCLE` to avoid reuse races across polling/worker paths.
