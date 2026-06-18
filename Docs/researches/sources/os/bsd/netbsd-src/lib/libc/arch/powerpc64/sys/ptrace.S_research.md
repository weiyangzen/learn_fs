# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/ptrace.S

This file implements PowerPC64 `ptrace` with errno pre-clearing. Reentrant builds save LR and arguments, call `__errno`, clear it, restore arguments, and then trap; non-reentrant builds clear TOC-addressed global `errno`.

After the syscall it returns on success or enters inline error handling on failure. The pre-clear is required for successful `ptrace` calls that return `-1`.
