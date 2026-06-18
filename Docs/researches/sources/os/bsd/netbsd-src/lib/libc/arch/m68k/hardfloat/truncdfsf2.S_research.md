# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/truncdfsf2.S

This helper implements `__truncdfsf2`, converting a double argument to single precision by loading it into the FPU and storing a single result for non-SVR4 ABI.
