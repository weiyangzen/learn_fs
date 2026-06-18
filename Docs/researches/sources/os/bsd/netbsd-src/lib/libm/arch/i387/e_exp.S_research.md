# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_exp.S

i387 double `exp` kernel. It computes `e^x` as `2^(x*log2(e))`, temporarily forcing x87 round-to-nearest/high precision if needed, then uses `frndint`, `f2xm1`, and `fscale`.

It explicitly handles NaN and infinities, returning zero for `-Inf`.
