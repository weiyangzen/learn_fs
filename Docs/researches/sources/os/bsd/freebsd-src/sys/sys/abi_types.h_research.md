# File Research: sources/os/bsd/freebsd-src/sys/sys/abi_types.h

ABI compatibility scalar type definitions.

Key elements:
- Defines `freebsd32_uint64_t`, represented as two 32-bit words on amd64 and as `uint64_t` elsewhere.
- Defines `time32_t`, 32-bit on amd64/i386 and 64-bit elsewhere.
- Defines `__HAVE_TIME32_T`.

Dependencies:
- Includes `sys/_types.h`.

Research notes:
- Captures FreeBSD-specific 32-bit ABI quirks, especially i386 time and 64-bit alignment behavior.
