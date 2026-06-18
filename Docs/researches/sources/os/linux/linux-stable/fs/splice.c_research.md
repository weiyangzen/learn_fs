# File Research: sources/os/linux/linux-stable/fs/splice.c

## Purpose
Linux VFS splice/vmsplice/tee implementation. It implements zero-copy or low-copy data movement through pipes, file-to-pipe, pipe-to-file, pipe-to-pipe, socket splice, direct splice for sendfile/copy_file_range, and vmsplice user-memory pipe integration.

## Pipe Buffer Operations
- `pipe_clear_nowait()` clears `FMODE_NOWAIT` from pipe files because splice does not support it.
- Page-cache pipe buffer ops:
  - `page_cache_pipe_buf_confirm()` verifies uptodate page-cache folios and handles truncated/unhashed folios as `-ENODATA`.
  - `page_cache_pipe_buf_try_steal()` tries to remove a folio from page cache after writeback/release checks.
  - `page_cache_pipe_buf_release()` drops page ref and clears LRU flag.
- User-page pipe buffer ops allow stealing only when `PIPE_BUF_FLAG_GIFT` is present.
- `default_pipe_buf_ops` and `nosteal_pipe_buf_ops` provide generic buffer behavior.

## Splice Into Pipe
- `splice_to_pipe()` installs pages from a `splice_pipe_desc` into a pipe until full or descriptor exhausted, handling no-readers with `SIGPIPE`/`-EPIPE`.
- `add_to_pipe()` inserts one prepared `pipe_buffer` or releases it on failure.
- `splice_grow_spd()` / `splice_shrink_spd()` manage dynamic descriptor arrays when pipe capacity exceeds default buffers.
- `copy_splice_read()` is fallback read-copy-to-pipe logic for O_DIRECT/DAX or read paths that cannot use page cache splicing.

## Splice From Pipe
- `splice_from_pipe_feed()` walks pipe buffers, confirms them, calls an actor, advances offsets/lengths, releases consumed buffers, and tracks wakeups.
- `splice_from_pipe_next()` waits for readable pipe data, respects `SPLICE_F_NONBLOCK`, signals, EOF, and empty buffers.
- `__splice_from_pipe()` is the generic loop over `next` and `feed`.
- `splice_from_pipe()` wraps it with pipe locking.
- `iter_file_splice_write()` builds bvec arrays from pipe buffers and writes through `->write_iter`, then consumes written pipe data.
- Under `CONFIG_NET`, `splice_to_socket()` sends pipe pages to sockets via `MSG_SPLICE_PAGES`, using `MSG_MORE` when appropriate.

## Direct Splice
- `do_splice_read()` validates readable input, caps reads by pipe space and `MAX_RW_COUNT`, uses `copy_splice_read()` for O_DIRECT/DAX, otherwise calls `->splice_read`.
- `vfs_splice_read()` wraps `rw_verify_area()` then `do_splice_read()`.
- `splice_direct_to_actor()` implements non-pipe to non-pipe transfer through a per-task cached pipe (`current->splice_pipe`), used by sendfile-like paths.
- It requires seekable input and drains the internal pipe through an actor to avoid stuck pipe data.
- `do_splice_direct()` uses a direct actor with `file_start_write()`/`file_end_write()`.
- `splice_file_range()` is the copy-file-range variant where the caller already holds write-start state.
- EOF notification is supported through `splice_eof`.

## Splice Syscall Routing
- `do_splice()` selects behavior:
  - pipe -> pipe: `splice_pipe_to_pipe()`
  - pipe -> file: validate write area, reject append, call `do_splice_from()`
  - file -> pipe: validate read area, call `splice_file_to_pipe()`
  - non-pipe -> non-pipe: invalid for `splice(2)`
- It updates offsets, honors pipe/nonblock flags, and emits fsnotify access/modify on success.
- `__do_splice()` handles userspace offsets and clears NOWAIT on pipe endpoints.
- `SYSCALL_DEFINE6(splice)` validates flags, fds, zero length, then calls `__do_splice()`.

## vmsplice
- `iter_to_pipe()` pins/gets pages from a source iterator with `iov_iter_get_pages2()` and inserts them as user-page pipe buffers.
- `vmsplice_to_pipe()` optionally marks buffers as gifts, waits for pipe space, inserts iterator pages, wakes readers, and sends modify notification.
- `vmsplice_to_user()` copies pipe pages to a destination user iterator via `__splice_from_pipe()` and `pipe_to_user()`.
- `SYSCALL_DEFINE4(vmsplice)` imports user iovecs, chooses source/destination mode from file permissions, and dispatches to pipe or user copy path.

## Pipe-to-Pipe and tee
- `ipipe_prep()` waits for readable input pipe data.
- `opipe_prep()` waits for writable output pipe space and handles no-reader `SIGPIPE`.
- `splice_pipe_to_pipe()` moves pipe buffers from input to output, partially copying buffer refs when only part of a buffer is requested. It uses `pipe_double_lock()` to avoid ABBA deadlocks.
- `link_pipe()` duplicates pipe buffer references into another pipe without consuming input; it clears gift and merge flags on output buffers.
- `do_tee()` validates pipe endpoints and uses `link_pipe()` for zero-copy duplication.
- `SYSCALL_DEFINE4(tee)` validates flags/fds/length and calls `do_tee()`.

## Important Semantics
- Pipe locking and wakeups are carefully separated between readers/writers and fasync notifications.
- `SPLICE_F_NONBLOCK` affects waiting on pipe readiness/space; direct splice deliberately clears nonblock for output drain.
- Gifted pages may be stolen only through user-page pipe ops and only once; cloned pipe buffers clear gift/merge flags.
- Page-cache splicing must coordinate with folio writeback and mapping removal to avoid filesystem corruption.
