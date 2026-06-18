# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrintf.S

ARM VFP `lrintf` implementation. `_lrintf` converts `s0` with `vcvtr.s32.f32`, moves the integer result to `r0`, and exposes `lrintf` as a weak alias.
