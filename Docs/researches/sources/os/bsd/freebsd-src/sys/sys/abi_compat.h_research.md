# File Research: sources/os/bsd/freebsd-src/sys/sys/abi_compat.h

ABI object translation helper macros.

Key elements:
- Defines pointer conversion macros `PTRIN` and `PTROUT`.
- Defines copy helpers for same-name fields, renamed fields, pointer fields, `timeval`, `timespec`, `itimerspec`, fixed 64-bit fields, and bintime-like fields.
- Uses static assertions for fixed 64-bit copies.

Dependencies:
- Includes `sys/abi_types.h`.
- Requires `uintptr_t`, `uint64_t`, and `memcpy` availability from context.

Research notes:
- Intended for syscall and compatibility layers translating structures between ABIs.
- Important for 32/64-bit kernel-user compatibility.
