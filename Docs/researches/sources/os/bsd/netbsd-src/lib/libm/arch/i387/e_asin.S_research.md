# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_asin.S

i387 `__ieee754_asin` implementation. It computes `sqrt(1 - x*x)` and uses `fpatan` with the original argument to produce asin.
