# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_msgctl.S

Defines the m68k compatibility `msgctl` entry point. It emits a link-time warning telling callers to include `<sys/msg.h>` for the correct modern reference.

The actual implementation is a `PSEUDO(msgctl, compat_14_msgctl)` syscall veneer, routing old `msgctl` references to the NetBSD 1.4 compatibility syscall.

No filesystem logic is present; this is System V IPC ABI compatibility.
