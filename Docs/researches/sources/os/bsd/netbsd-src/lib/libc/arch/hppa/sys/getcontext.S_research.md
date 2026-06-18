# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/getcontext.S

This HPPA `getcontext` wrapper invokes the syscall, then adjusts saved PC queue head/tail entries in the ucontext to point at the caller return address and next instruction. It also stores zero into the saved return-value register.
