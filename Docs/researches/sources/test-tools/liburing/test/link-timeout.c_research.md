# sources/test-tools/liburing/test/link-timeout.c

Purpose: comprehensive linked-timeout regression suite covering timeout cancellation, invalid linked timeout placement, update operations, poll/read chains, and kernel-version-dependent return codes.

Important APIs/types/functions: `io_uring_prep_link_timeout`, `io_uring_prep_timeout`, `io_uring_prep_timeout_update`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_poll_add`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_ASYNC`, `IORING_LINK_TIMEOUT_UPDATE`, `__kernel_timespec`, and `mtime_since_now`.

Control flow: `main()` runs many focused subtests. It checks standalone linked timeouts reject with `-EINVAL`, timeout-to-timeout chains, NOP/read/poll heads with link timeouts, chains where timeouts cancel later links, and `timeout_update` for valid and missing target IDs. Pipe reads and polls provide operations that either block until timeout or complete after a paired write.

State and persistence behavior: no persistent storage. State is per-ring linked request lists, timeout target identity via `user_data`, cancellation propagation, pipe readiness, and wall-clock duration of timeout update.

Dependencies and integration points: depends on liburing helpers, pipe and poll semantics, and kernel behavior that may return acceptable alternatives such as `-EALREADY`, `-ETIME`, `-EINTR`, `-ECANCELED`, or `-EINVAL` on different paths.

Risks and test signals: failures identify broken timeout arming, cancellation propagation, invalid SQE validation, timeout update lookup, or link-chain termination. The update test also asserts elapsed time is roughly 10-200 ms after shortening a five-second timeout.
