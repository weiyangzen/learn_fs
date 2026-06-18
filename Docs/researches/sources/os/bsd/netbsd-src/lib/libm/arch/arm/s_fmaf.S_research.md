# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fmaf.S

ARM VFP float fused multiply-add helper. `_fmaf` performs `s2 += s0 * s1` with `vmla.f32`, moves the result to `s0`, and exports `fmaf` as a weak alias.
