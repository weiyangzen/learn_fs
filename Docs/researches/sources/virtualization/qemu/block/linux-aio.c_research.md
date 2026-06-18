# File Research: sources/virtualization/qemu/block/linux-aio.c

## Role

`block/linux-aio.c` implements QEMU's Linux native AIO backend using `libaio`. It provides coroutine submission for raw read/write/flush-like operations, batches pending requests, handles kernel completion events through an `eventfd`, resubmits short reads/writes, and integrates with QEMU's AioContext polling and bottom-half mechanisms.

## Core Structures

`qemu_laiocb` is the per-request state:
- submitting coroutine,
- `LinuxAioState`,
- kernel `struct iocb`,
- result,
- offset and byte count,
- original and resubmission iovecs,
- fd, request type, flags,
- device-specific max batch,
- queue linkage.

`LaioQueue` tracks pending and in-flight requests, queue blockage, and recursion depth.

`LinuxAioState` owns:
- QEMU AioContext,
- kernel `io_context_t`,
- event notifier,
- request queue,
- completion bottom half,
- nested completion iteration indices.

## Submission Queue

Requests enter through `laio_co_submit()`, which stack-allocates `qemu_laiocb`, calls `laio_do_submit()`, and yields until completion.

`laio_do_submit()` prepares the kernel iocb:
- `QEMU_AIO_WRITE`: `io_prep_pwritev2` with `RWF_DSYNC` for FUA when built with support, otherwise `io_prep_pwritev`.
- `QEMU_AIO_ZONE_APPEND`: `io_prep_pwritev`.
- `QEMU_AIO_READ`: `io_prep_preadv`.
- `QEMU_AIO_FLUSH`: `io_prep_fdsync`.

The iocb is tied to the backend eventfd with `io_set_eventfd()`, queued, and submitted immediately if batch thresholds are met. Otherwise `defer_call()` schedules deferred submission.

`ioq_submit()` submits batches up to `MAX_EVENTS` and the configured max batch. It handles:
- `-EAGAIN` by leaving the queue blocked,
- other submission errors by failing the first pending request,
- partial successful submission by splitting the pending queue,
- immediate completion processing when requests are in flight.

`IOQ_SUBMIT_MAX_DEPTH` caps recursive submit/completion cycles caused by synchronous completions and nested event loops.

## Completion Handling

The backend reads the kernel AIO ring directly through `io_getevents_peek()`, `io_getevents_commit()`, and `io_getevents_advance_and_peek()`. The comments note this copies Linux's AIO ring ABI and uses a read memory barrier paired with kernel completion ordering.

`qemu_laio_process_completions()` supports nested event loops by storing iteration indices in `LinuxAioState`, scheduling a completion BH before processing, and resetting indices once done.

`qemu_laio_process_completion()` converts kernel results:
- exact completion returns `0`,
- short read/write resubmits the remaining tail through `laio_resubmit_short_io()`,
- read EOF zero-fills the rest of the iovec,
- write zero-byte completion and zone-append short/nonfull completion become `-ENOSPC`,
- cancellation result `-ECANCELED` is preserved.

The coroutine is awakened unless it is already entered, avoiding recursive coroutine entry.

## AioContext Integration

`laio_attach_aio_context()` creates the completion BH and registers the event notifier with callback, poll, and poll-ready hooks. `laio_detach_aio_context()` removes the notifier and deletes the BH.

`qemu_laio_completion_cb()` processes completions when the eventfd fires. `qemu_laio_poll_cb()` lets QEMU poll readiness by peeking at the ring. `qemu_laio_poll_ready()` processes completions from polling paths.

## Initialization and Capability Checks

`laio_init()` allocates state, initializes the event notifier, creates the kernel AIO context with `MAX_EVENTS`, and initializes the queue. `laio_cleanup()` cleans up the event notifier, destroys the kernel AIO context, and frees state.

`laio_has_fdsync()` probes whether the host kernel accepts `IO_CMD_FDSYNC` by submitting a one-entry fdsync command to a temporary AIO context.

`laio_has_fua()` returns true only when built with `HAVE_IO_PREP_PWRITEV2`, because FUA is represented through `RWF_DSYNC`.

## Important Constraints

- Queue depth is capped at `MAX_EVENTS` per backend.
- Submissions may be batched globally by `aio_max_batch` and per-device by `dev_max_batch`.
- The code assumes access from the AioContext home thread; queue structures are not separately locked.
- FUA support depends on build-time availability of `io_prep_pwritev2`.
