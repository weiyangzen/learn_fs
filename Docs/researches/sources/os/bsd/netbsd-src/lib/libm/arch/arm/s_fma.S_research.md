# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fma.S

ARM VFP double fused multiply-add wrapper. `_fma` performs `d2 += d0*d1`, moves `d2` to `d0`, and aliases `fma` and long-double `fmal` symbols.
