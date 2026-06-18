# sources/test-tools/liburing/test/epwait.c

Purpose: tests `IORING_OP_EPOLL_WAIT` for ready, delayed, deletion, closed-epoll, racing, defer-taskrun, and SQPOLL cases. Important APIs are `io_uring_prep_epoll_wait`, epoll/pipes, pthread writer, atomic stop flag, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_SQPOLL`.

Control flow: build epoll sets around pipes, run immediate ready and delayed writer cases, delete an fd while waiting, close epoll while wait is pending, then run a 1000-completion race with eight pipes and verify user_data ordering. Main repeats across ring modes. State is epoll interest lists and pipe buffers. Risks are unsupported op, stale fd state, lost CQEs, negative results, or user_data mismatch.
