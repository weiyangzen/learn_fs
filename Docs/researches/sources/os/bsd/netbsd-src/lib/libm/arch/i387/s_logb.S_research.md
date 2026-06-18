# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logb.S

i387 double `logb` implementation. It uses `fxtract`, discards the significand, and returns the unbiased exponent as a floating-point value.
