# File Research: sources/os/linux/linux/io_uring/eventfd.h

## Purpose
Declares io_uring eventfd registration and signaling functions.

## Main Contents
- Forward declaration for `struct io_ring_ctx`.
- Prototypes for `io_eventfd_register()`, `io_eventfd_unregister()`, and `io_eventfd_signal()`.

## Cross-File Relationships
- Implemented by `eventfd.c`.
- Used by io_uring registration and completion paths.

## Risks / Review Notes
- `io_eventfd_signal()` takes a `cqe_event` boolean that changes suppression semantics; callers must choose it consistently.
