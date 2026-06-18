# sources/user-network-fs/nfs-utils/support/nfs/atomicio.c

Purpose: robust read/write loop that attempts to transfer exactly `n` bytes through a supplied I/O function.

Important API: `ssize_t atomicio(ssize_t (*f)(int, void *, size_t), int fd, void *_s, size_t n)` accepts a `read`- or `write`-compatible function pointer and returns bytes transferred, zero, or `-1`.

Control flow: loops until `pos == n`. `EINTR` and `EAGAIN` retry immediately. A zero result or nonretryable error returns a partial count if any bytes were already transferred; otherwise it returns the underlying zero or error.

State and persistence: no state beyond local counters; no persistence.

Dependencies and integration: includes `nfslib.h` and libc `errno`/`unistd` APIs. It is a generic helper for socket or file descriptor protocols requiring complete fixed-size transfers.

Risks: retrying `EAGAIN` without polling can spin on nonblocking descriptors. The callback signature uses `void *`, so direct use with `write()` may require a cast that discards constness. Returning a partial byte count on error requires callers to distinguish partial success from complete success.

Test signals: interrupted I/O, short reads/writes, EOF before any bytes, EOF after partial bytes, nonretryable errno, and nonblocking `EAGAIN` behavior.
