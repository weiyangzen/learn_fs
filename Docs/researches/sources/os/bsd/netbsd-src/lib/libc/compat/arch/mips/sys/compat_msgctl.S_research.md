# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_msgctl.S

Defines MIPS compatibility `msgctl`.

It emits a compatibility warning and maps `msgctl` to `compat_14_msgctl`.

No filesystem logic is present.
