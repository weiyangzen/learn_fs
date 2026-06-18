# sources/test-tools/liburing/test/open-close.c

Purpose: tests io_uring open and close operations, including relative/absolute openat, closing normal and ring fds, fixed-file close, close flush, and direct-open `O_CLOEXEC` rejection.

Important APIs/types/functions: `io_uring_prep_openat`, `io_uring_prep_close`, `__io_uring_set_target_fixed_file`, `io_uring_register_files`, `test_close_fixed`, `test_close_flush`, `test_open_direct_cloexec`, `t_create_file`, `O_CLOEXEC`, and `IOSQE_FIXED_FILE`.

Control flow: creates `/tmp/.open.close` and optionally a relative file, opens both via io_uring, closes the returned fd, attempts to close the ring fd expecting wait failure/`-EBADF`, exercises fixed-file close error and success cases, optionally closes tracing `trace_pipe_raw`, and ensures direct open with `O_CLOEXEC` fails with `-EINVAL`.

State and persistence behavior: creates temporary files and unlinks them. Fixed-file table slots are mutated and verified by a subsequent fixed-file read returning `-EBADF`.

Dependencies and integration points: depends on file permissions, optional debugfs tracing file, fixed-file close support, and helpers for creating files.

Risks and test signals: skip on unsupported open or access-restricted files. Failures include wrong close error codes, fixed table not invalidated, or direct open accepting incompatible flags.
