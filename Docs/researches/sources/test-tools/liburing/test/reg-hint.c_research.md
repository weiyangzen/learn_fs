# sources/test-tools/liburing/test/reg-hint.c

Purpose: verifies direct descriptor allocation fails safely after unregistering the sparse file table. It targets stale allocation-hint state after `io_uring_unregister_files()`.

Important APIs and types: `io_uring_register_files_sparse`, `io_uring_unregister_files`, `io_uring_prep_socket_direct_alloc`, `io_uring_submit`, `io_uring_wait_cqe`, and socket constants `AF_UNIX`/`SOCK_DGRAM`.

Control flow: `main()` initializes a one-entry ring, registers a sparse file table with 16 slots, unregisters it, then submits `io_uring_prep_socket_direct_alloc()` to allocate an `AF_UNIX` datagram socket into a direct descriptor slot. Since no file table is registered anymore, the CQE must complete with `-ENFILE`.

State and persistence: the sparse file table registration is intentionally removed before the socket-direct allocation. The test checks that no stale table or hint persists in a way that allows allocation or crashes.

Dependencies and integration: requires sparse file table registration and socket-direct allocation. `-EINVAL` from sparse file registration is treated as feature unsupported and skipped.

Risks and test signals: any CQE result other than `-ENFILE` is a failure. Passing demonstrates direct allocation correctly sees the absence of a registered file table after unregister.
