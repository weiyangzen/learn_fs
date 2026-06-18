# sources/test-tools/liburing/test/connect-rep.c

Purpose: regression test that repeated connects to a bound non-listening loopback socket return `-ECONNREFUSED`. Important APIs are `io_uring_prep_connect`, loopback `bind`/`getsockname`, `io_uring_queue_init_params`, and SQPOLL setup.

Control flow: create a server socket bound but not listening, create a client socket, optionally let SQPOLL sleep, and issue 32 connect attempts in normal and SQPOLL rings. The sockaddr copy is overwritten after submit to detect stale userspace address use. Risk is wrong error translation, stale address handling, or SQPOLL-specific behavior.
