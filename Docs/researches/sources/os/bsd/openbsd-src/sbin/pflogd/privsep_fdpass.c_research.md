# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/privsep_fdpass.c

## Purpose

Small fd-passing utility for `pflogd` privilege separation.

## Behavior

`send_fd()` sends an integer result over a Unix domain socket. If the fd is valid, it attaches the fd using `SCM_RIGHTS`; if invalid, it sends the current `errno` as the result code without ancillary fd data.

`receive_fd()` reads the integer result and optional control message. A zero result requires an `SCM_RIGHTS` control message and returns the received fd. A nonzero result is copied into `errno` and returns `-1`.

## Risks And Invariants

- Both sides expect exactly `sizeof(int)` bytes of normal payload.
- The receiver warns if no control header appears or if the control type is not `SCM_RIGHTS`.
- The code does not validate `cmsg_level`; it checks only `cmsg_type`.
