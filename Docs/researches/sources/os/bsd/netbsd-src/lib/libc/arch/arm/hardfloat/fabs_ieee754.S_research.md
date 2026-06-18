# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fabs_ieee754.S

This VFP assembly file implements both `fabsl` and `fabs` entries by applying `vabs.f64 d0, d0` and returning. It requires the VFP assembler mode through `.fpu vfp`.
