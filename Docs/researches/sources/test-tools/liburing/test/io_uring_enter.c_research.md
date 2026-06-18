<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_enter.c -->
## sources/test-tools/liburing/test/io_uring_enter.c

Purpose: low-level unit tests for the `io_uring_enter` syscall ABI and SQ ring drop accounting.

Important APIs/types/functions: `expect_fail`, `try_io_uring_enter`, `setup_file`, `io_prep_read`, `reap_events`, `submit_io`, raw `io_uring_enter`, `t_io_uring_init_sqarray`, `io_uring_smp_store_release`, and SQ fields `ktail`, `khead`, `kdropped`.

Control flow: the test initializes a large SQ-array ring, verifies invalid flags/fds and valid no-op enter behavior, fills the SQ with readv requests, calls enter with `IORING_ENTER_GETEVENTS` and `min_complete` equal to SQ depth, verifies all completions are available, then manually writes an invalid SQ array index and checks the kernel increments the dropped counter.

State and persistence behavior: temporary `/tmp/io_uring_enter-test.XXXXXX` file backs the read requests and is unlinked after submission. SQ ring memory is directly modified for the invalid-index test.

Dependencies and integration points: bypasses high-level submit helpers for syscall ABI and ring memory ordering validation.

Risks: direct SQ manipulation is fragile but intentional. If large ring setup fails with `-ENOMEM`, it falls back to 128 entries.

Test signals: pass means syscall error handling, GETEVENTS waiting, completion accounting, and invalid SQE drop accounting work.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_enter.c -->
