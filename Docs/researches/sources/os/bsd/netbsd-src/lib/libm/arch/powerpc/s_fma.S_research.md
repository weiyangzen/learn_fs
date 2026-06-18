# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fma.S

PowerPC double fused multiply-add. `fma` uses `fmadd %f1, %f1, %f2, %f3`, returns with `blr`, and weak-aliases `fmal` to `fma` when supported.
