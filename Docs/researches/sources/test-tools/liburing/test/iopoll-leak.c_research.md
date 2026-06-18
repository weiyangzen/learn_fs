<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-leak.c -->
## sources/test-tools/liburing/test/iopoll-leak.c

Purpose: regression test for memory/resource leaks when an IOPOLL ring exits with submitted IO not explicitly completed.

Important APIs/types/functions: `do_iopoll`, `test`, `fork`, `wait`, `t_create_ring(... IORING_SETUP_IOPOLL)`, and `io_uring_prep_read`.

Control flow: `main` creates or uses a direct-IO file and runs 16 child processes. Each child opens the file with O_DIRECT, creates one aligned buffer, initializes an IOPOLL ring, submits a read, then closes the fd and frees the buffer without waiting for completion or exiting the ring explicitly.

State and persistence behavior: each child leaks/abandons an in-flight IOPOLL request by design; process exit performs final cleanup. The temporary file is removed by the parent.

Dependencies and integration points: depends on O_DIRECT and IOPOLL support.

Risks: does not verify CQEs; leak detection requires external sanitizers/kernel accounting. Unsupported direct IO skips.

Test signals: pass means repeated abandoned IOPOLL submissions do not cause visible process failure; deeper leak signal comes from surrounding test infrastructure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-leak.c -->
