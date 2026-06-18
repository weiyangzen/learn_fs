<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_register.c -->
## sources/test-tools/liburing/test/io_uring_register.c

Purpose: low-level unit tests for the `io_uring_register` syscall ABI, buffer limits, file-table limits, and ring-fd registration restrictions.

Important APIs/types/functions: `expect_fail`, `new_io_uring`, `map_filebacked`, `test_max_fds`, `test_memlock_exceeded`, `test_iovec_nr`, `test_iovec_size`, `ioring_poll`, `test_poll_ringfd`, raw `io_uring_register`, `IORING_REGISTER_BUFFERS`, and `IORING_REGISTER_FILES`.

Control flow: `main` verifies invalid fd/opcode handling, then tests buffer registration error cases: null base, zero length, partially unmapped memory, huge pages, file-backed memory, memlock pressure, and excessive iovec count. It then attempts very large file registration using a huge mapped fd array, and finally verifies polling the ring fd works while registering the ring fd as a fixed file fails.

State and persistence behavior: tracks page size, memlock rlimit, and `/dev/null` fd globally. It maps large anonymous/file-backed regions and unmaps them after file-table tests.

Dependencies and integration points: covers syscall ABI, memory pinning, rlimits, filesystem mapping type detection, poll, SQPOLL, and fixed-file validation.

Risks: resource-heavy; many cases depend on memlock limits, hugepages, address-space availability, and root/non-root behavior.

Test signals: pass means registration rejects invalid inputs, accepts supported boundary cases, and protects against ring-fd fixed-file registration.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_register.c -->
