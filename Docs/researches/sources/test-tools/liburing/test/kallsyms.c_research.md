<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/kallsyms.c -->
## sources/test-tools/liburing/test/kallsyms.c

Purpose: exercises `/proc/kallsyms` read file operations through io_uring with vectored/non-vectored and registered/non-registered buffers.

Important APIs/types/functions: `__test_io`, `test_io`, `has_nonvec_read`, `io_uring_register_probe`, `io_uring_prep_read`, `io_uring_prep_readv`, `io_uring_prep_read_fixed`, and `t_register_buffers`.

Control flow: the test allocates one 8192-byte aligned buffer, probes non-vectored read opcode support, then reads `/proc/kallsyms` with readv and read paths, both with and without registered buffers as supported. It waits for each CQE and tolerates `-EINVAL` on unsupported non-vectored reads.

State and persistence behavior: global `vecs` hold buffers and `warned` suppresses repeated unsupported messages. `/proc/kallsyms` content is read-only kernel symbol state.

Dependencies and integration points: integrates procfs file operations, registered buffers, opcode probing, and standard ring setup.

Risks: `/proc/kallsyms` may be unavailable or permission-restricted; those cases are treated as nonfatal returns. The test does not validate data content.

Test signals: pass means procfs read handlers work through io_uring's read/readv/fixed-buffer paths.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/kallsyms.c -->
