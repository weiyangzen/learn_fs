# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/SYS.h

This header defines or1k syscall wrapper macros. It loads syscall numbers into `r13`, uses `l.sys 0`, treats the branch flag as the error indicator, and supplies `_SYSCALL`, `PSEUDO`, `RSYSCALL`, and `WSYSCALL`.

It also uses generated `NSYSARGS_*` macros to load seventh and eighth syscall arguments from the stack into `r11` and `r12` before trapping. This generated-argument-count dependency is specific and important for correct syscall marshalling.
