# sources/test-tools/liburing/test/close-opath.c

Purpose: checks io_uring close behavior for ordinary and `O_PATH` descriptors. Key APIs are `openat`, `O_PATH`, `io_uring_prep_close`, `io_uring_submit`, and `io_uring_wait_cqe`.

Control flow: initialize a small ring, open `.` with `O_RDONLY` and `O_PATH`, submit close operations, and flag unexpected negative CQE results while tolerating known unsupported/invalid/EBADF outcomes. State is only transient fds. Risk is close regression for `O_PATH` fds or unexpected error handling changes.
