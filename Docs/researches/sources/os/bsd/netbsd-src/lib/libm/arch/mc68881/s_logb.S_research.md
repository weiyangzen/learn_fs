# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_logb.S

mc68881 double `logb`. It handles NaN/infinity/zero specially, using `fabsx`, `flog2x`, or `fgetexpx` to return the appropriate exponent-like value.
