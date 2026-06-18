# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__vfork14.S

This ARM `__vfork14` wrapper preserves the link register in `r2`, invokes the syscall, and normalizes the fork-style return convention: parent receives the child pid, child receives zero. It returns through the saved `r2`.
