# sources/test-tools/fio/os/windows/posix/include/sys/socket.h

Purpose: empty `<sys/socket.h>` shim for Windows.

Important APIs/types: none; socket definitions are expected from Winsock headers.

Control flow and state: no runtime behavior.

Dependencies and integration: satisfies Unix include paths in fio networking code.

Risks: not sufficient for code that includes only `<sys/socket.h>` and expects POSIX socket APIs or constants.

Test signals: Windows network build coverage with current include ordering.
