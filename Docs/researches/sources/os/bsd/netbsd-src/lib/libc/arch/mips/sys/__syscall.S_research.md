# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__syscall.S

This file defines `__syscall` through `RSYSCALL(__syscall)`. For non-o32 MIPS ABIs it also aliases `_syscall` and weak `syscall` to `__syscall`; o32 has a separate `syscall.S`.

It is generic syscall-number dispatch glue. Its detailed trap/error behavior comes from `SYS.h`.
