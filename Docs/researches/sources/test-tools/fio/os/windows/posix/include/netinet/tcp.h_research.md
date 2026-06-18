# sources/test-tools/fio/os/windows/posix/include/netinet/tcp.h

Purpose: empty `<netinet/tcp.h>` shim for Windows fio builds.

Important APIs/types: none.

Control flow and state: no logic or state.

Dependencies and integration: satisfies include directives when TCP constants are obtained through Winsock or not used in Windows code paths.

Risks: missing constants such as `TCP_NODELAY` if future code expects this header to provide them.

Test signals: Windows build coverage of network code that includes `<netinet/tcp.h>`.
