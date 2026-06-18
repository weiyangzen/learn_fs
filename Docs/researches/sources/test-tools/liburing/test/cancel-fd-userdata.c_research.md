# sources/test-tools/liburing/test/cancel-fd-userdata.c

Purpose: validates cancellation matching by both file descriptor and user_data, including fixed-file cancellation and duplicate user_data across fds. Key APIs are `io_uring_prep_poll_add`, `io_uring_prep_cancel`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_USERDATA`, `IORING_ASYNC_CANCEL_FD_FIXED`, and fixed-file registration.

Control flow: submit multiple pipe polls, cancel only the targeted `(fd, user_data)` request while tolerating CQE ordering, clean up remaining polls, repeat for fixed fds, then test two-fd discrimination. State is pending poll request identity. Risks are unsupported flags, overbroad cancellation, missing CQEs, or wrong result codes.
