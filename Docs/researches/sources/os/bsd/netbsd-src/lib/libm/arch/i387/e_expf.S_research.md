# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_expf.S

i387 float `expf` kernel. It uses the same `2^(x*log2(e))` x87 algorithm as the double version and has explicit NaN/infinity handling, including zero for `-Inf`.
