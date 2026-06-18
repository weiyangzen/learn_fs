# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_msgctl.S

Defines SPARC64 compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue compatibility.
