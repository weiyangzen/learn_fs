# sources/test-tools/fio/os/windows/posix/include/poll.h

Purpose: declares a minimal `poll()` interface for Windows.

Important APIs/types: includes `<winsock2.h>`, typedefs `nfds_t` as `int`, and declares `poll(struct pollfd[], nfds_t, int)`.

Control flow and state: `posix.c` implements `poll()` by translating event masks into `select()` read/write/exception sets and writing `revents`.

Dependencies and integration: depends on Winsock's `struct pollfd` and socket constants. Used by fio client/server or network paths.

Risks: `select()` receives `nfds` even though Windows ignores that value; only `POLLIN`, `POLLOUT`, and exception-as-`POLLHUP` are modeled. File-descriptor polling is not supported, only sockets.

Test signals: network readiness tests on readable, writable, closed, invalid, and timeout sockets.
