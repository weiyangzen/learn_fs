# sources/test-tools/fio/os/windows/posix.h

Purpose: minimal umbrella header for Windows POSIX compatibility declarations that are not provided by the local include shims.

Important APIs/types: defines `clockid_t` as `int` and declares `inet_aton()` plus `win_to_posix_error(DWORD)`. The declarations support Windows code that expects Unix-ish networking and errno conversion helpers.

Control flow and state: no executable logic or state lives here; it only makes compatibility symbols visible to other compilation units.

Dependencies and integration: assumes Windows `DWORD` is already visible through included Windows headers. It is paired with `posix.c` and the `os/windows/posix/include` shim headers.

Risks: because it does not include the Windows header that defines `DWORD` or the networking header that defines `struct in_addr`, including this header in isolation may fail. It is meant for the existing fio include order.

Test signals: successful Windows compilation is the main signal; include-order tests would catch missing transitive definitions.
