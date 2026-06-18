# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1p.S

i387 double `log1p`. It selects between `fyl2xp1` for small `|x|` and `fyl2x` on `1+x` for other inputs, using `ln(2)` as the scale factor.
