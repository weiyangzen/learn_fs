# File Research: sources/os/linux/linux/io_uring/eventfd.c

## Purpose
Implements eventfd registration, unregistration, and CQ event signaling for io_uring.

## Main Structures
- `struct io_ev_fd`: holds the registered eventfd context, async-only flag, last CQ tail seen, refs, pending operation bits, and RCU callback.

## Main Functions
- `io_eventfd_register()`: installs an eventfd for a ring, initializes last CQ tail, flags, refs, and RCU pointer.
- `io_eventfd_unregister()`: clears ring eventfd state and drops the reference.
- `io_eventfd_signal()`: signals the registered eventfd when completions are posted, respecting disabled CQ flags and async-only mode.
- Internal helpers manage RCU freeing and deferred signaling when direct eventfd signaling is not allowed.

## Important Design Points
- Eventfd state is RCU-protected through `ctx->io_ev_fd`.
- `eventfd_async` restricts signaling to io-wq workers.
- `cqe_event` mode avoids signaling if `cached_cq_tail` did not advance since the last eventfd signal.
- If `eventfd_signal_allowed()` is false, signaling is deferred via RCU callback and `call_rcu_hurry()`.

## Cross-File Relationships
- Declared in `eventfd.h`.
- Uses `io_wq_current_is_worker()` from `io-wq.h`.
- Integrated with io_uring register/unregister operations and completion posting.

## Risks / Review Notes
- Reference handling is split between RCU readers and deferred callbacks; missing `io_eventfd_put()` would leak.
- Signal suppression based on CQ tail is important because applications may rely on eventfd count changing only when new CQEs appear.
