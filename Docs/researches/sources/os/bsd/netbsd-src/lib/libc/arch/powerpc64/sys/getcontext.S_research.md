# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext` for PowerPC64. It calls the kernel `getcontext`, then stores LR into the saved PC field and zero into the saved `%r3` return-value field.

It uses offsets from `assym.h` and the PowerPC64 syscall macro layer. The adjustment ensures a restored context resumes as a successful `getcontext` return.
