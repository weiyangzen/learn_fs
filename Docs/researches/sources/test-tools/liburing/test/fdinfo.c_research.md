<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo.c -->
## sources/test-tools/liburing/test/fdinfo.c

Purpose: broad regression test that performs io_uring read/write workloads while repeatedly reading `/proc/self/fdinfo` for the ring.

Important APIs/types/functions: `fdinfo_read`, `__test_io`, `test_io`, `has_nonvec_read`, `test_eventfd_read`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, `t_register_buffers`, `io_uring_register_files`, `IORING_SETUP_SQPOLL`, and `IORING_SETUP_SQE_MIXED`.

Control flow: the main matrix creates a test file and buffers, probes non-vectored read support, then runs read/write combinations across buffered/direct IO, SQPOLL fixed files, registered buffers, mixed SQE sizes, and non-vectored operations. Each workload flushes SQ state, reads fdinfo before and during submission, and validates completions. It also tests eventfd reads under normal, defer-taskrun, and SQPOLL rings.

State and persistence behavior: global `vecs`, `no_read`, and `warned` track buffers and feature skips. Temporary files are unlinked after the matrix.

Dependencies and integration points: combines procfs fdinfo rendering with active ring state, fixed resources, buffer selection-like paths, and eventfd IO.

Risks: large feature matrix can skip selectively. fdinfo reads are diagnostic but must not perturb SQ/CQ state.

Test signals: pass means fdinfo inspection is safe while varied io_uring workloads are live.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo.c -->
