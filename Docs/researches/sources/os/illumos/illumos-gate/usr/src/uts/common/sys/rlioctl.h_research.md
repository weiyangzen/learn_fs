# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rlioctl.h

## Role

`rlioctl.h` defines rlogin STREAMS module ioctl and packet-control constants.

## Constants

The header supplies fallback definitions for `TRUE` and `TIOCPKT_WINDOW`, then defines rlogin-relevant packet bits:
- `TIOCPKT_FLUSHWRITE`
- `TIOCPKT_NOSTOP`
- `TIOCPKT_DOSTOP`

`RLOGIN_MAGIC` is `0xff`, matching RFC 1282’s two-byte magic prefix for rlogin protocol requests.

The ioctl namespace is `RLIOC`, with `RL_IOC_ENABLE` used to start the module and optionally insert provided data at the head of the read-side queue.

## Research Notes

This is a small protocol-control header for rlogin STREAMS support. Its important surface is the packet bit compatibility with pty packet mode and RFC 1282 magic-byte handling.
