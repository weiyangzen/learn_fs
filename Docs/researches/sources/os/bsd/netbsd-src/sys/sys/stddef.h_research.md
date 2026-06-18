# File Research: sources/os/bsd/netbsd-src/sys/sys/stddef.h

Read completely: 156 lines.

This C common-definitions header declares `ptrdiff_t`, `size_t`, `max_align_t`, `wchar_t`, C23 `nullptr_t`, `NULL`, C23 `unreachable`, and `offsetof`. It also defines `__STDC_VERSION_STDDEF_H__` for NetBSD/C23 modes.

`max_align_t` is a union aligned for pointer, long double, and long long. `offsetof` uses `__builtin_offsetof` for modern GCC, a C null-pointer member address fallback otherwise, and a C++ reinterpret-cast fallback for older compilers.

Risks: type exposure depends on machine-provided `_BSD_*` macros and language standard mode. The fallback `offsetof` forms are compatibility paths for older compilers.
