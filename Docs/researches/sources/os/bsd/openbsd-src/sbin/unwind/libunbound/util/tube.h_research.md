# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.h

Defines the tube message-pipe abstraction.

Key types:
- `tube_callback_type`: callback receiving tube, message pointer, length, error code, and user argument.
- `struct tube`: platform-specific state.
  - Unix: read/write fds, background comm points, read state, write queue.
  - Winsock: callback state, WSA event, optional event wrapper, lock, and FIFO queue.
- `struct tube_res_list`: queued message node with buffer and length.

Public API:
- Lifecycle and fd control: `tube_create`, `tube_delete`, `tube_close_read`, `tube_close_write`, `tube_read_fd`.
- Synchronous framed I/O: `tube_write_msg`, `tube_read_msg`.
- Readiness: `tube_poll`, `tube_wait`, `tube_wait_timeout`.
- Async setup: `tube_setup_bg_listen`, `tube_remove_bg_listen`, `tube_setup_bg_write`, `tube_remove_bg_write`, `tube_queue_item`.
- Callback entry points for function-pointer whitelisting: `tube_handle_listen`, `tube_handle_write`, `tube_handle_signal`.

Usage notes:
- Queued message buffers are freed by the tube machinery after writing or removal.
- The header explicitly warns not to mix direct read/write style with background style for the same direction.
