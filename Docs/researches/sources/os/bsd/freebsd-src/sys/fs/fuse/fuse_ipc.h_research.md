# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.h

This header defines the FUSE IPC/session data structures, queue primitives, mount/session flags, dispatcher API, and inline helpers for feature negotiation and cache mode.

Key structures:
- `enum fuse_data_cache_mode`
  - `FUSE_CACHE_UC`: uncached/direct.
  - `FUSE_CACHE_WT`: write-through cache.
  - `FUSE_CACHE_WB`: writeback cache.
- `struct fuse_iov`
  - Holds variable-size message buffers with current length, allocation size, and shrink credit.
- `struct fuse_ticket`
  - Represents one FUSE request/reply transaction.
  - Holds unique id, session pointer, flags, refcount, optional interrupt request id, outgoing message buffer, message-queue link, incoming answer buffer/header/error, answer mutex, answer handler, and answer-queue link.
- `struct fuse_data`
  - Represents one mounted/open FUSE session.
  - Holds device, mount, root vnode, daemon credentials, session flags, refcount, message queue, answer queue, unique-id counter, negotiated ABI, readahead/write/read limits, select/kqueue state, daemon timeout, Linux errno mode, time granularity, implemented/not-implemented opcode masks, mount flags, and cache mode.
- `struct fuse_dispatcher`
  - Convenience wrapper around a ticket, input header, payload pointer, request size, node id, answer status, and answer pointer.

Important flags:
- Session lifecycle and security:
  - `FSESS_DEAD`
  - `FSESS_INITED`
  - `FSESS_DAEMON_CAN_SPY`
  - `FSESS_PUSH_SYMLINKS_IN`
  - `FSESS_DEFAULT_PERMISSIONS`
  - `FSESS_INTR`
  - `FSESS_AUTO_UNMOUNT`
- Negotiated daemon capabilities:
  - `FSESS_ASYNC_READ`
  - `FSESS_POSIX_LOCKS`
  - `FSESS_EXPORT_SUPPORT`
  - `FSESS_SETXATTR_EXT`
- One-shot warning bits:
  - short write
  - wrote too much
  - xattr list issues
  - cache incoherency
  - illegal inode
  - embedded NUL readlink
  - dot lookup mismatch
  - inode/nodeid mismatch

Queue helpers:
- Message queue:
  - `fuse_ms_push`
  - `fuse_ms_push_head`
  - `fuse_ms_pop`
- Answer queue:
  - `fuse_aw_push`
  - `fuse_aw_remove`
  - `fuse_aw_pop`
- These helpers take/release extra ticket references while tickets are queued.

Feature/cache helpers:
- `fsess_is_impl`, `fsess_maybe_impl`, `fsess_not_impl`, `fsess_set_impl`, `fsess_set_notimpl`.
- `fsess_opt_datacache`, `fsess_opt_mmap`, and `fsess_opt_writeback`.
- `fuse_libabi_geq` for negotiated protocol checks.
- `fdata_get_dead` tests dead sessions.

Declared APIs:
- Buffer management: `fiov_init`, `fiov_teardown`, `fiov_refresh`, `fiov_adjust`.
- Ticket management: `fuse_ticket_fetch`, `fuse_ticket_drop`.
- Queue/dispatch: `fuse_insert_callback`, `fuse_insert_message`.
- Response pull: `fticket_pull`.
- Warning/session lifecycle: `fuse_warn`, `fdata_alloc`, `fdata_trydestroy`, `fdata_set_dead`.
- Dispatcher construction/wait: `fdisp_make`, `fdisp_make_vp`, `fdisp_refresh_vp`, `fdisp_wait_answ`, `fdisp_simple_putget_vp`.

Integration points:
- Used by every FUSE operation-building layer.
- The device node implementation depends on the queue layout and ticket fields.
- Mount and init code stores negotiated capabilities in `struct fuse_data`.

Notable risks and research hooks:
- `notimpl` and `isimpl` are 64-bit opcode bitmasks, so opcode values must remain within usable range for this representation.
- Queue helpers require their corresponding mutexes to be held.
- Ticket lifetime relies on balanced references from callers and queue insertion/removal.
- `FSESS_MNTOPTS_MASK` defines which session flags are mount-option controlled and checked during remount.
