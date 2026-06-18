# sources/test-tools/fio/engines/rbd.c

## Purpose
`rbd.c` implements fio's `rbd` ioengine for benchmarking Ceph RADOS Block Device images through librbd. It turns a configured RBD image into a fio file-like target, discovers image size with `rbd_stat`, and submits async read/write/discard/flush operations through librbd completions.

## Important APIs, Types, And Functions
`struct fio_rbd_iou` is per-`io_u` state with the librbd completion and two completion flags. `struct rbd_data` stores Ceph cluster, pool IO context, RBD image handle, event arrays, optional poll eventfd, and connection state. `struct rbd_options` exposes cluster, image, pool, client, busy-poll, and optional encryption settings.

`_fio_setup_rbd_data()` allocates engine arrays. `_fio_rbd_connect()` opens the Ceph cluster, pool, image, configures cache behavior for direct I/O, optionally loads encryption, and optionally installs RBD poll notification. `_fio_rbd_finish_aiocb()` maps librbd completion return values into fio error/resid state. `rbd_iter_events()` polls completion state either through `rbd_poll_io_events()` plus eventfd or by scanning fio's in-flight `io_u`s and waiting oldest-first. `fio_rbd_queue()` submits `rbd_aio_read`, `rbd_aio_write`, `rbd_aio_discard`, or `rbd_aio_flush`.

## Control Flow
`.setup` allocates state, forces thread mode because librbd cannot cross fork boundaries, connects in the main context, gets image size, and creates a synthetic fio file if necessary. `.init` reconnects only if setup did not already leave `connected` true. Each I/O creates a librbd completion with `_fio_rbd_finish_aiocb` as callback, submits based on `ddir`, then returns queued. `.getevents` loops until at least `min` completions are discovered, optionally busy-spinning when `busy_poll` is enabled. `.event` returns entries from `aio_events`.

## State And Persistence
The RBD image is persistent; the engine does not create or delete images. It may alter client-side cache behavior and may load image encryption. Completion state is stored in each `fio_rbd_iou` and released when observed. `sort_events` is a temporary oldest-first wait list for non-poll mode.

## Dependencies And Integration Points
Dependencies include `librbd`, `librados`, optional `CONFIG_RBD_ENCRYPTION`, optional `CONFIG_RBD_POLL`, Linux `poll/eventfd`, and fio's ioengine lifecycle. The engine registers as `rbd` with fio's option group `FIO_OPT_G_RBD`.

## Risks
The non-poll path scans all in-flight `io_u`s and depends on callback-updated flags without explicit atomics, so portability depends on fio/librbd threading assumptions. Poll mode decrements the eventfd semaphore best-effort and logs but continues on read failure. Encryption options are accepted even when unsupported, but then fail connect. `fio_rbd_io_u_free()` does not release an outstanding completion if an I/O is freed unexpectedly; normal completion release happens in `fri_check_complete()`.

## Test Signals
Test coverage should include image open failures, encryption option rejection/loading, direct-I/O cache disable behavior, read/write/discard/flush completion, busy-poll versus blocking behavior, and poll-notification builds. Full tests require a Ceph cluster with an RBD image; allocation and option parsing can be unit-tested in isolation.
