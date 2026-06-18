# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/misc/arm_initfini.c

This constructor initializes ARM AAPCS runtime feature flags used by libc code such as `setjmp`. It queries `machdep` sysctl nodes for `fpu_present` and, when the compiler target lacks architectural integer divide, `hwdiv_present`, storing results in hidden globals and guarding repeated initialization.
