# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/atomicio.c

`atomicio.c` implements robust full-buffer I/O helpers. `atomicio()` repeatedly calls `read` or write-compatible functions until the requested byte count is transferred, interrupted operations retry, `EAGAIN` waits with `poll()`, and EOF sets `EPIPE`.

`atomiciov()` does the same for `readv`/`writev`, copying and mutating an iovec array as partial transfers complete. It rejects `iovcnt > IOV_MAX`.

These helpers are used by `ldattach` relay mode to avoid short writes while copying data between tty and pty fds.
