<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-iter.c -->
## sources/test-tools/liburing/test/fixed-buf-iter.c

Purpose: verifies fixed-buffer read/write with non-iterator file operations, based on a liburing issue regression.

Important APIs/types/functions: `test`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `/dev/urandom`, and `/dev/zero`.

Control flow: the test opens `/dev/urandom` and `/dev/zero`, allocates a 4096-byte buffer, registers it, reads random data into it via `read_fixed`, then writes it to `/dev/zero` via `write_fixed`, validating both CQEs are nonnegative.

State and persistence behavior: one fixed buffer remains registered during both IO operations. The file descriptors and buffer are local resources; the ring exits in `main`.

Dependencies and integration points: targets fixed-buffer support for character devices whose file operations do not use normal iterators.

Risks: cleanup is incomplete on some error paths. It validates success/nonnegative result rather than exact byte counts.

Test signals: pass means fixed-buffer IO can traverse non-iterator read/write implementations without kernel failure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-iter.c -->
