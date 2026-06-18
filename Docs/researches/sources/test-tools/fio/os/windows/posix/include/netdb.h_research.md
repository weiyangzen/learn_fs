# sources/test-tools/fio/os/windows/posix/include/netdb.h

Purpose: placeholder `<netdb.h>` for Windows fio builds.

Important APIs/types: none; it only satisfies include presence.

Control flow and state: no logic or state.

Dependencies and integration: used where source files include `<netdb.h>` unconditionally while actual needed networking declarations come from Winsock headers elsewhere.

Risks: any future code expecting `struct addrinfo`, `getaddrinfo()`, or `gai_strerror()` from this header will fail unless another header provides them first.

Test signals: compilation of current Windows networking code; add include-coverage tests if new netdb APIs are introduced.
