# File Research: sources/os/linux/linux/io_uring/refs.h

Small inline helper header for request reference counting.

Key responsibilities:
- Provides guarded increments/decrements for `struct io_kiocb::refs`.
- Supports normal put, atomic put-and-test, get, and initialize-to-one helpers.
- Detects zero or near-overflow reference values using the same style as page reference checking.

Important invariants:
- Refcount helpers warn unless `REQ_F_REFCOUNT` is set, except `req_ref_put_and_test()` fast-completes unrefcounted requests.
- `req_ref_zero_or_close_to_overflow()` protects against underflow and overflow-adjacent states.
- `__io_req_set_refcount()` initializes refs only once.
