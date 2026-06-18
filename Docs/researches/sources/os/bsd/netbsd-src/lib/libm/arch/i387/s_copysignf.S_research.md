# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysignf.S

x86 float `copysignf`. It combines the sign bit from the second argument with the magnitude of the first, using stack word operations on i386 and XMM masks on x86-64.
