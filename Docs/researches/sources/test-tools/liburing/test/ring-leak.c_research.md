# sources/test-tools/liburing/test/ring-leak.c

Purpose: regression coverage for io_uring lifetime leaks caused by SCM_RIGHTS transfer, registered-file cycles, and io-wq cancellation during ring teardown.

Important APIs/types/functions: raw `__sys_io_uring_setup`, `__sys_io_uring_register`, `IORING_REGISTER_FILES`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_queue_exit`, UNIX datagram `socketpair`, `SCM_RIGHTS`, and pipe reads as a quiescence signal.

Control flow: `test_iowq_request_cancel()` registers pipe fds, queues fixed-file reads including an async one, exits the ring, then verifies the registered write end eventually closes. `test_scm_cycles()` sends the ring fd over a UNIX socket, registers or updates a set containing pipes and socket endpoints, closes external references, exits the ring, triggers UNIX GC, and waits for EOF. `main()` also runs the original raw-ring SCM_RIGHTS cycle scenario around a fork.

State/persistence behavior: state is kernel-owned ring/file reference graphs rather than filesystem state. The tests deliberately create cycles among ring fds, registered file tables, UNIX sockets, pipes, and io-wq work.

Dependencies/integration: depends on UNIX ancillary fd passing, io_uring file registration, kernel garbage collection for UNIX sockets, and async ring teardown. `sendmsg` returning `EINVAL` is treated as an unsupported/skip path.

Risks/test signals: a bad kernel may hang, leak the ring, or keep pipe write ends alive. The test mostly signals by successful process exit and pipe EOF rather than by explicit memory accounting.
