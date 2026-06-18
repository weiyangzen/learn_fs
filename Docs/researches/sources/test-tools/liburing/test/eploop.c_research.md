# sources/test-tools/liburing/test/eploop.c

Purpose: prevents recursive event generation when an io_uring fd is added to epoll and the same ring polls that epoll fd. Important APIs are `epoll_create1`, `epoll_ctl`, `io_uring_prep_poll_multishot`, `io_uring_prep_nop`, and CQE wait/peek.

Control flow: add ring fd to epoll, submit multishot poll on epoll, submit NOP to make ring readable, reap two CQEs, then ensure no extra CQE exists. State is epoll interest in the ring fd and ring readiness. Risk is feedback-loop recursion producing excess completions.
