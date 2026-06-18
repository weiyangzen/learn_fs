# sources/test-tools/liburing/test/read-mshot-stdin.c

Purpose: provides an interactive multishot read test for stdin. It is intentionally skipped by the normal harness unless invoked with the single argument `stdin`, because it requires human or piped input and prints CQE details.

Important APIs and types: `io_uring_queue_init_params` with `IORING_SETUP_CQSIZE`, `io_uring_setup_buf_ring`, `io_uring_prep_read_multishot`, selected-buffer flags, `IORING_CQE_F_MORE`, and buffer IDs encoded in CQE flags. The ring uses one SQE and a CQ sized to 64 buffers.

Control flow: `test_stdin()` registers 64 32-byte buffers with bids 1 through 64, submits a multishot read on `STDIN_FILENO`, then loops waiting for completions. Nonzero completions must have a buffer flag. It prints result, bid, and flags, verifies positive completions use consecutive bids, and stops when `IORING_CQE_F_MORE` is absent.

State and persistence: `last_bid` tracks expected bid sequencing across completions. Buffer ring entries are consumed by stdin reads. No data content validation is attempted because input is external.

Dependencies and integration: requires buffer ring and multishot read support. Queue or buffer-ring `-EINVAL` is treated as skip. `main()` skips unless argv is exactly `stdin`.

Risks and test signals: missing buffer flags for data, non-consecutive bids, submission failures, or wait failures are test failures. Passing is an interactive signal that stdin multishot reads return buffered CQEs in expected bid order and terminate cleanly.
