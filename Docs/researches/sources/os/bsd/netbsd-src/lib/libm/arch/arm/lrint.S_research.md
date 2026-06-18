# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrint.S

ARM VFP `lrint` implementation for double input. It aliases `lrint`, `_lrint`, `lrintl`, and `_lrintl`, converts with `vcvtr.s32.f64`, moves the result to `r0`, and returns.
