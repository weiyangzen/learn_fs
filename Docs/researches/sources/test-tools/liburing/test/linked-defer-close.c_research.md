# sources/test-tools/liburing/test/linked-defer-close.c

Purpose: reproduces a deferred-taskrun close bug where a linked send chain with skipped CQEs must still close the accepted socket and wake a peer.

Important APIs/types/functions: `io_uring_prep_multishot_accept`, `io_uring_prep_send`, `io_uring_prep_close`, `IOSQE_CQE_SKIP_SUCCESS`, `IOSQE_IO_LINK`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, sockets, `pthread_create`, `SIGUSR1`, and `alarm`.

Control flow: main listens on port 9999, arms multishot accept, starts a client thread, then on accept submits three linked sends followed by a close, all success-CQEs skipped except the accept. The client reads until EOF and signals the parent with `SIGUSR1`; an alarm fails the test if EOF never arrives.

State and persistence behavior: no files. State is TCP socket lifetime, skipped CQE handling, and deferred taskrun completion while the submitter is in `cqring_wait`.

Dependencies and integration points: depends on loopback networking, multishot accept support, signal handling, and deferred taskrun support. `-EINVAL` setup or multishot accept returns skip.

Risks and test signals: failure is seeing unexpected skipped send/close CQEs, never receiving SIGUSR1, bind/listen/connect errors, or timeout after five seconds.
