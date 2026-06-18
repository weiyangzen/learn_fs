# sources/test-tools/liburing/test/self.c

Purpose: verifies async pathname resolution for `/proc/self` uses the original submitting task rather than an io-wq worker.

Important APIs/types/functions: `io_uring_prep_openat2`, `struct open_how`, `O_RDONLY`, `io_uring_submit`, `io_uring_wait_cqe`, `/proc/self/comm`, and normal `read`.

Control flow: `io_openat2()` submits one openat2 request and returns the CQE result fd or errno. `main()` opens `/proc/self/comm` through io_uring, reads it, and expects the command name to start with `self`.

State/persistence behavior: no durable state; it reads procfs task metadata. The tested state is the task context used by async path resolution.

Dependencies/integration: depends on kernel `openat2` support, procfs, and liburing openat2 prep helper. `-EINVAL` or `-EOPNOTSUPP` are treated as skip/success paths for older kernels.

Risks/test signals: a regression returns the worker comm rather than the test program name, or fails open/read. The assertion is narrow to process naming and may be affected by unusual invocation names.
