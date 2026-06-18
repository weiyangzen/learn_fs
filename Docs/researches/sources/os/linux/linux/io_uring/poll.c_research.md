# File Research: sources/os/linux/linux/io_uring/poll.c

io_uring poll and async-poll engine. This file implements pure poll requests, poll removal/update, poll-driven retry for other operations, cancellation, waitqueue wake handling, multishot behavior, and double-waitqueue support.

Key responsibilities:
- Arms poll requests using VFS `vfs_poll()` with an io_uring waitqueue callback.
- Tracks ownership through `req->poll_refs` with reference bits plus cancel and retry flags.
- Supports single and double waitqueue entries for files whose `poll()` registers multiple wait queues.
- Implements pure `IORING_OP_POLL_ADD`, `IORING_OP_POLL_REMOVE`, updates to user data/events, and async poll arming for other opcodes.
- Handles multishot poll CQEs and multishot read retry integration.
- Cancels poll requests by user data, file/op matching, task match, or ring teardown.

Important data flows:
- `__io_arm_poll_handler()` initializes poll state, calls `vfs_poll()`, registers wait queues through `_qproc`, inserts the request into `ctx->cancel_table`, and decides whether it completed inline or should wait.
- `io_poll_wake()` filters wake masks, handles `POLLFREE`, optionally removes oneshot wait entries, and schedules `io_poll_task_func`.
- `io_poll_check_events()` rechecks readiness, posts multishot CQEs, reissues poll-backed operations, or completes/removes requests.
- `io_poll_remove()` disarms an existing poll request and either updates/rearms it or completes it with `-ECANCELED`.

Concurrency and locking:
- Waitqueue removal uses RCU plus waitqueue head locks to tolerate `wake_up_pollfree()` and RCU-delayed waitqueue freeing.
- Cancel-table insertion/removal is guarded by `ctx->uring_lock`.
- Ownership via `poll_refs` prevents races between arming, wake callbacks, task_work, and cancellation.
- Double-poll setup serializes against the first waitqueue lock before adding the second entry.

Important invariants:
- `IO_POLL_UNMASK` events are always included so error/hangup conditions are observed.
- `EPOLLONESHOT` is added unless multishot/level semantics require otherwise.
- `REQ_F_SINGLE_POLL` and `REQ_F_DOUBLE_POLL` describe which waitqueue entries must be removed.
- Circular io_uring wakeups force oneshot behavior to avoid self-triggering multishot loops.

Notable risks:
- Request lifetime depends on waitqueue removal, hash removal, and poll reference ownership happening in the right order.
- `POLLFREE` can arrive while another path owns the request, so the callback must cancel, kick task_work, and detach from the waitqueue carefully.
- Async poll retries are capped to prevent repeated poll-triggered issue failure loops.
