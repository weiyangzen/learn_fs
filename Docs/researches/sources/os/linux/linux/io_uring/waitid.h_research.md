# File Research: sources/os/linux/linux/io_uring/waitid.h

Header for asynchronous io_uring waitid support.

Key responsibilities:
- Defines `struct io_waitid_async`, holding the owning request and kernel `wait_opts`.
- Declares waitid prep/issue, cancel, and remove-all helpers.
- Includes kernel exit internals for `wait_opts`.

Important invariant:
- The async wait state owns the waitqueue entry embedded in `wait_opts`.
