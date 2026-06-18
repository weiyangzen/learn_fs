# sources/test-tools/liburing/test/socket-nb.c

Purpose: verifies empty-socket recv returns immediate `-EAGAIN` only when `MSG_DONTWAIT` is set, independent of the socket fd `O_NONBLOCK` flag.

Important APIs/types/functions: TCP loopback setup, `t_set_nonblock`, `t_clear_nonblock`, `io_uring_prep_recv`, `MSG_DONTWAIT`, `io_uring_peek_cqe`, and `SO_ERROR` connect polling.

Control flow: `test()` builds a connected TCP pair, optionally marks the receiving fd nonblocking, queues one recv with or without `MSG_DONTWAIT`, and peeks for completion. `main()` runs all four combinations of fd nonblocking and message flag.

State/persistence behavior: only socket readiness and ring state are used. No data is sent, so the recv should be pending unless `MSG_DONTWAIT` forces immediate completion.

Dependencies/integration: uses TCP loopback and liburing recv. The test expects peek to return `-EAGAIN` for pending CQE, not necessarily socket `-EAGAIN`.

Risks/test signals: catches incorrect treatment of `O_NONBLOCK` as enough for immediate CQE, failure to honor `MSG_DONTWAIT`, or unexpected completions.
