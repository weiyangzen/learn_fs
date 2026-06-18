# File Research: sources/os/linux/linux/io_uring/timeout.h

Header for io_uring timeout state and operations.

Key responsibilities:
- Defines `struct io_timeout_data`, containing request pointer, hrtimer, time, mode, and flags.
- Declares timeout flush, cancel, kill, queue-linked, disarm, prep, issue, remove-prep, and remove issue helpers.

Important invariant:
- Timeout helpers participate in cancellation and linked-request completion, so callers must honor documented completion and timeout lock ordering.
