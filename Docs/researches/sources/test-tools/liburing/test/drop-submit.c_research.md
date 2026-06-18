# sources/test-tools/liburing/test/drop-submit.c

Purpose: tests `IORING_SETUP_SUBMIT_ALL` batch semantics with invalid SQEs. Important APIs are `IORING_SETUP_SUBMIT_ALL`, NOP prep, invalid read prep, bad `ioprio`, and `io_uring_submit`.

Control flow: queue four NOPs and two invalid reads; with submit-all expect six submitted, without it expect five. State is only the SQ submission batch, and CQEs are not reaped. Risks are unsupported submit-all and regressions in invalid-SQE drop/continue behavior.
