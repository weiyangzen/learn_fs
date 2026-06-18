# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor_fdpass.c

This file implements descriptor passing helpers for isakmpd monitor/process separation.

Key APIs:
- `mm_send_fd(int socket, int fd)`: sends one file descriptor over a Unix-domain socket using `sendmsg(2)` with `SCM_RIGHTS`.
- `mm_receive_fd(int socket)`: receives one descriptor using `recvmsg(2)` and returns the passed fd.

Behavior and integration:
- Uses `struct msghdr`, `struct cmsghdr`, `CMSG_SPACE`, `CMSG_LEN`, and a one-byte iovec payload because ancillary data requires a real message payload.
- Depends on `log_error()` for failure reporting and `monitor.h` for exported declarations.
- Validates send/receive byte count is exactly one and checks that received control message type is `SCM_RIGHTS`.

Risk notes:
- `mm_receive_fd()` checks `cmsg_type` but does not explicitly validate `cmsg_level == SOL_SOCKET` or `cmsg_len`; malformed local control messages could be rejected less strictly than ideal.
- This code assumes a trusted local IPC channel between isakmpd processes.
