# sources/test-tools/fio/os/windows/posix/include/arpa/inet.h

Purpose: Windows replacement for the POSIX `<arpa/inet.h>` subset used by fio.

Important APIs/types: includes `<ws2tcpip.h>` and `<inttypes.h>`, typedefs `socklen_t` and `in_addr_t` to `int`, maps `EAI_SYSTEM` to `EAI_FAIL`, and declares `inet_network()`.

Control flow and state: header-only declarations and macros; runtime behavior is in Winsock and `posix.c`.

Dependencies and integration: lets fio code include `<arpa/inet.h>` on Windows while still receiving Winsock definitions such as `inet_pton()` and address structures. `inet_network()` is implemented in `posix.c`; `inet_aton()` may come from `oslib/inet_aton.c` or `posix.h`.

Risks: `in_addr_t` is normally an unsigned IPv4 address type, but this shim uses `int`; callers that rely on exact signedness or width may behave differently. The `EAI_SYSTEM` mapping discards the Unix convention of consulting `errno`.

Test signals: compile Windows network paths and run server/client address parsing with IPv4 literals and failing `getaddrinfo()` cases.
