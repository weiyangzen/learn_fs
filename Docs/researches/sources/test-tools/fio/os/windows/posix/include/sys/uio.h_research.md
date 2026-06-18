# sources/test-tools/fio/os/windows/posix/include/sys/uio.h

Purpose: declares vector I/O types for Windows fio builds.

Important APIs/types: `struct iovec` contains `iov_base` and `iov_len`; declares `readv()` and `writev()`.

Control flow and state: `posix.c` stubs `readv()` with `ENOSYS`; `writev()` loops over vectors and sends each segment on a Winsock socket.

Dependencies and integration: used by network code that writes scatter/gather buffers. Includes `<unistd.h>` for `ssize_t`.

Risks: `writev()` is socket-only and does not preserve atomic vector-write semantics. `readv()` is unavailable on Windows. Callers must avoid general file descriptor vector I/O.

Test signals: socket writev behavior with multiple vectors and error injection; verify read paths do not require `readv()`.
