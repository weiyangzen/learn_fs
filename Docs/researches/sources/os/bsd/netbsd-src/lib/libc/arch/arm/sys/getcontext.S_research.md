# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/getcontext.S

This ARM `getcontext` wrapper preserves the ucontext pointer across the syscall, updates the saved program counter with the current link register, arranges saved `r0` to be zero, and returns zero. Softfloat state saving is noted as incomplete in comments.
