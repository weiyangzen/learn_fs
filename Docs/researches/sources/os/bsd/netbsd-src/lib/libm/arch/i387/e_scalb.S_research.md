# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalb.S

i387 double `__ieee754_scalb` implementation. It loads the scale and value, applies x87 `fscale`, drops the scale value from the FP stack, and returns the scaled double.
