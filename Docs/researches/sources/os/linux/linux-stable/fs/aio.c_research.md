# File Research: sources/os/linux/linux-stable/fs/aio.c

## Purpose
Implements the legacy Linux native asynchronous I/O syscalls and their completion ring: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents` including compat/time32 variants.

## Main Components
- `struct kioctx`: per-AIO-context state, completion ring, refs, wait queue, active cancellation list, request counters, and mmap metadata.
- `struct aio_ring`: user-visible ring header plus `io_event` array.
- `struct aio_kiocb`: internal request wrapper for read/write, fsync, and poll operations.
- Private pseudo filesystem and ring file used to back mmaped ring pages.
- Sysctl state for global `aio-nr` and `aio-max-nr`.

## Important Behavior
`io_setup()` allocates a `kioctx`, creates and mmaps ring folios, installs the context in the current mm’s RCU-protected ioctx table, and charges the global AIO request quota. Context lifetime is split between `users` and `reqs` percpu refs: user refs protect lookup/submission, while request refs keep the context alive until all in-flight requests finish.

Ring overflow is avoided with `reqs_available`, batched through per-cpu counters. Completed events are written under `completion_lock`; userspace advances `ring->head`, while the kernel updates `tail`. `aio_read_events_ring()` copies events to userspace and advances the ring head under `ring_lock`.

`io_submit()` supports pread/pwrite, preadv/pwritev, fsync/fdatasync, and poll. Reads/writes use file `read_iter`/`write_iter`; fsync is punted to workqueue with captured creds; poll handles waitqueue lifetime, `POLLFREE`, cancellation, inline completion, and workqueue fallback.

## State And Synchronization
Uses `mm->ioctx_lock`, RCU lookup, percpu refs, `ctx_lock` for active requests/cancel, `ring_lock` for ring reads and migration coordination, `completion_lock` for event insertion, and wait queues for `io_getevents()`. Ring folio migration is supported with a private address-space operation and synchronized against teardown through `aio_inode_info::migrate_lock`.

## Risks / Review Notes
The ring protocol is intentionally shared with userspace, so head/tail ordering and barriers are critical. Poll cancellation and `POLLFREE` rely on waitqueue lock ordering plus RCU-delayed freeing. Error paths after partial request setup must balance eventfd refs, file refs, request slots, and percpu request refs exactly.
