# File Research: sources/os/linux/linux/fs/splice.c

Implements Linux VFS splice, vmsplice, tee, direct splice, and pipe-buffer helper machinery. It moves data between files, pipes, sockets, and user iterators using pipe buffers as the central transport abstraction, with zero-copy where possible and fallback copying where required.

Major areas:
- Pipe buffer operations:
  - `page_cache_pipe_buf_ops` supports page-cache buffers with confirm, release, steal, and get operations.
  - `page_cache_pipe_buf_try_steal()` locks the folio, waits for writeback, releases filesystem-private state, removes the folio from mapping, and marks it LRU when stealing succeeds.
  - `page_cache_pipe_buf_confirm()` validates page-cache data is uptodate and handles truncated/unhashed folios with `-ENODATA`.
  - `user_page_pipe_buf_ops` allows stealing only gifted user pages.
  - `default_pipe_buf_ops` and `nosteal_pipe_buf_ops` cover generic and socket-like buffers.
- Filling pipes:
  - `splice_to_pipe()` inserts a `splice_pipe_desc` page array into a pipe and releases unused pages.
  - `add_to_pipe()` appends one `pipe_buffer` or releases it on `EPIPE`/`EAGAIN`.
  - `splice_grow_spd()` and `splice_shrink_spd()` size temporary page/partial arrays to pipe capacity.
  - `copy_splice_read()` allocates pages, reads through `->read_iter()`, and inserts copied pages into a pipe; used for O_DIRECT and DAX sources.
- Draining pipes:
  - `splice_from_pipe_feed()`, `splice_from_pipe_next()`, `splice_from_pipe_begin()`, and `splice_from_pipe_end()` implement the generic pipe-to-actor loop with signal, nonblock, EOF, wakeup, and buffer-release handling.
  - `__splice_from_pipe()` exports the unlocked generic loop.
  - `splice_from_pipe()` wraps it with pipe locking.
  - `iter_file_splice_write()` writes pipe buffers to files through `->write_iter()` using bvec iterators.
  - `splice_to_socket()` sends pipe pages to sockets with `MSG_SPLICE_PAGES` when `CONFIG_NET` is enabled.
- File and direct splice:
  - `do_splice_read()` validates read mode, clamps length to pipe space and `MAX_RW_COUNT`, selects `copy_splice_read()` for O_DIRECT/DAX, otherwise calls file `->splice_read`.
  - `vfs_splice_read()` performs `rw_verify_area()` then `do_splice_read()`.
  - `splice_direct_to_actor()` implements sendfile/direct copy through a per-task cached internal pipe.
  - `do_splice_direct()` supports sendfile-style file-to-file transfer and wraps output writes in `file_start_write()`.
  - `splice_file_range()` provides the copy-file-range helper variant where the caller already started the write.
- `splice(2)` syscall:
  - `do_splice()` dispatches pipe-to-pipe, pipe-to-file, file-to-pipe, or invalid non-pipe/non-pipe cases; handles offsets, `FMODE_PREAD/PWRITE`, append rejection, `rw_verify_area()`, nonblock propagation, write accounting, f_pos updates, and fsnotify events.
  - `__do_splice()` copies user offsets in/out, rejects offsets on pipe ends, clears `FMODE_NOWAIT` on pipe files, and calls `do_splice()`.
  - `SYSCALL_DEFINE6(splice)` validates flags, fds, zero length, and delegates to `__do_splice()`.
- `vmsplice(2)`:
  - `iter_to_pipe()` pins/imports user iterator pages in chunks, creates user-page pipe buffers, and supports `SPLICE_F_GIFT`.
  - `vmsplice_to_pipe()` waits for pipe space, maps user pages into the pipe, wakes readers, and sends modify notification.
  - `vmsplice_to_user()` copies pipe data to a user iterator via `pipe_to_user()`; reverse vmsplice is implemented as copying rather than VM remapping.
  - `SYSCALL_DEFINE4(vmsplice)` imports user iovecs as source or destination depending on file mode and dispatches accordingly.
- Pipe-to-pipe and tee:
  - `ipipe_prep()` and `opipe_prep()` wait for readable input and writable output with signal/nonblock handling.
  - `splice_pipe_to_pipe()` moves or partially copies pipe buffers between two pipes, avoiding ABBA deadlock with `pipe_double_lock()`, clearing gifted/merge flags for partial references, and waking readers/writers.
  - `link_pipe()` duplicates pipe buffer references without consuming input, used by tee.
  - `do_tee()` validates pipe endpoints and duplicates pipe contents with fsnotify events.
  - `SYSCALL_DEFINE4(tee)` validates flags/fds/length and calls `do_tee()`.

Important invariants:
- Pipe locks protect head/tail manipulation; pipe-to-pipe paths use address-ordered double locking to avoid deadlocks.
- `splice_direct_to_actor()` must drain its internal pipe before returning; output side is forced blocking even if input nonblock is requested.
- Offsets are invalid for pipe ends and require seek-capable file modes for regular files.
- `O_APPEND` outputs are rejected for splice-to-file/direct splice because explicit offsets and append semantics conflict.
- `pipe_clear_nowait()` strips `FMODE_NOWAIT` from pipe file modes because splice itself does not support NOWAIT semantics.
- Partial pipe-buffer duplication clears `PIPE_BUF_FLAG_GIFT` and `PIPE_BUF_FLAG_CAN_MERGE` to avoid multiple steals or unsafe merging.
- `-ENODATA` from confirming a truncated page-cache buffer is treated as zero-byte progress/EOF-like behavior in splice feed paths.

Exported symbols include:
- `splice_to_pipe()`
- `add_to_pipe()`
- `copy_splice_read()`
- `default_pipe_buf_ops`
- `nosteal_pipe_buf_ops`
- `__splice_from_pipe()`
- `iter_file_splice_write()`
- `vfs_splice_read()`
- `splice_direct_to_actor()`
- `do_splice_direct()`
- `splice_file_range()`

Maintenance notes:
- This file is central VFS code with many subtle user-visible errno, blocking, signal, and notification semantics. Changes should be checked against splice/vmsplice/tee syscall behavior, pipe wakeups, and file position update rules.
- Page stealing is filesystem-sensitive; the writeback wait and `filemap_release_folio()`/`remove_mapping()` sequence protects against corruption when removing page-cache folios.
- `copy_splice_read()` maps `-EFAULT` from `read_iter()` to `-EAGAIN` to satisfy splice caller expectations when no pipe data could be produced.
