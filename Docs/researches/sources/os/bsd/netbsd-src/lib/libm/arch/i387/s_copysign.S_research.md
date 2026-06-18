# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysign.S

x86 double `copysign`. i386 edits the sign bit in stack argument words; x86-64 masks sign and magnitude in XMM registers with constants, then ORs them together.
