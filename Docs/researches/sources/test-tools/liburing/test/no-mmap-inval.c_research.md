# sources/test-tools/liburing/test/no-mmap-inval.c

Purpose: verifies `IORING_SETUP_NO_MMAP` rejects an invalid user-provided SQ/CQ mapping layout.

Important APIs/types/functions: `io_uring_queue_init_params`, `IORING_SETUP_NO_MMAP`, `io_uring_params.cq_off.user_addr`, `t_posix_memalign`, `sysconf(_SC_PAGESIZE)`, `-EFAULT`, and `-ENOMEM`.

Control flow: allocates one page-aligned 8 KiB area, sets only the CQ user address in params, and tries to initialize a no-mmap ring. Unsupported kernels returning `-EINVAL` or `-ENOENT` skip; expected invalid mapping returns `-EFAULT` or sometimes `-ENOMEM`.

State and persistence behavior: one allocated userspace buffer is freed. No ring should be successfully persisted.

Dependencies and integration points: depends on no-mmap setup support and helper allocation. It directly probes kernel validation of user ring addresses.

Risks and test signals: any return other than unsupported skip, expected fault, or memory failure is a test failure, as it suggests bad validation or changed error semantics.
