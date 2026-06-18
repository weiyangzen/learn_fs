# File Research: sources/os/bsd/freebsd-src/sys/sys/utsname.h

`uname(3)` ABI header.

Key responsibilities:
- Defines `SYS_NMLN` as 32 in kernel for FreeBSD 1.1 ABI compatibility, or 256 by default for userland unless already overridden.
- Defines `struct utsname` fields for OS name, node name, release, version, and machine type.
- Declares variable-record-size `__xuname()`.
- Provides inline `uname()` wrapper passing `SYS_NMLN` to `__xuname`.

Dependencies:
- Includes `sys/cdefs.h`.

Notable risks:
- The structure size depends on `SYS_NMLN`, so the inline wrapper and `__xuname` length parameter are central to compatibility.
