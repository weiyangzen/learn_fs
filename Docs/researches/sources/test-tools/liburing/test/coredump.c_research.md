# sources/test-tools/liburing/test/coredump.c

Purpose: liveness regression ensuring a process with pending io_uring async work can segfault/core-dump without hanging. Important APIs are `fork`, `wait`, `pipe`, `io_uring_queue_init`, `io_uring_prep_read`, and `IOSQE_ASYNC`.

Control flow: child submits an async pipe read and dereferences NULL; parent waits and removes `core`. State may include a generated core file. Sanitizer builds skip. Test signal is absence of hang rather than detailed signal verification.
