# sources/test-tools/liburing/test/poll-cancel-all.c

Purpose: validates async cancel flags for cancel-all-by-fd, fixed fd cancellation, cancel-any across mixed poll/read operations, and selective cancellation among multiple fds.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_cancel`, `io_uring_prep_read`, `IORING_ASYNC_CANCEL_ALL`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_FD_FIXED`, `IORING_ASYNC_CANCEL_ANY`, `IOSQE_FIXED_FILE`, and `IOSQE_ASYNC`.

Control flow: `test1()` arms eight polls on one pipe and cancels all by fd, including fixed-file mode. `test2()` arms polls on two pipes and cancels one fd at a time, checking no extra CQEs leak. `test3()` cancels mixed async polls with CANCEL_ANY. `test4()` cancels eight async pipe reads. Main runs these on one ring after creating a pipe.

State and persistence behavior: transient pipes, optional fixed-file registrations, and in-flight poll/read requests.

Dependencies and integration points: depends on cancel flag support; `-EINVAL` on cancel completion sets `no_cancel_flags` and skips later flag-specific tests.

Risks and test signals: expected cancel CQE counts are exact: 8, 4, 8, or 8 depending on test. Poll/read CQEs must report `-ECANCELED`; extra or missing completions are failures.
