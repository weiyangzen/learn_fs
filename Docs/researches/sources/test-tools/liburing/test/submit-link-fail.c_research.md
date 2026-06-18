# sources/test-tools/liburing/test/submit-link-fail.c

Purpose: tests linked requests that fail during submission/preparation and verifies later linked requests are canceled or preserved according to link/drain/hardlink rules.

Important APIs/types/functions: `IOSQE_IO_LINK`, `IOSQE_IO_HARDLINK`, `IOSQE_IO_DRAIN`, invalid fd reads with bad `ioprio`, pipe-backed drain blocker, `io_uring_submit`, and CQE result checks.

Control flow: `test_underprep_fail()` creates a fresh ring, optionally queues a draining pipe read, queues a link chain where one request is deliberately invalid, submits, tolerates old early-under-submit behavior, otherwise unblocks drain and verifies the drain CQE, failing request CQE, and canceled linked requests. `main()` runs small link sizes/failure indexes across hardlink, drain, and link-last combinations.

State/persistence behavior: only ring state and pipe fds are used. Each scenario uses a new ring because failures can leave dirty queue state.

Dependencies/integration: covers kernel linked-submit error handling and CQE cancellation semantics.

Risks/test signals: catches wrong submit counts, invalid failed-request result, missing cancellations, drain misuse, or kernel fault conditions from partially prepared linked SQEs.
