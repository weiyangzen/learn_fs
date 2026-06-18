# sources/test-tools/liburing/test/conn-unreach.c

Purpose: verifies io_uring connect/shutdown results for an unreachable IPv4 target. Important APIs are `io_uring_prep_connect`, `io_uring_prep_shutdown`, `getsockopt(SO_ERROR)`, TCP timeout sockopts, and nonblocking sockets.

Control flow: configure a TCP socket for quick failure, submit connect to `172.31.5.5:12345`, wait briefly, submit shutdown, and accept connect `-ECONNRESET`/`-ENETUNREACH` plus shutdown success/`-ENOTCONN`. State is transient socket error state. Risks are network-environment variability and unsupported connect returning `-EINVAL`.
