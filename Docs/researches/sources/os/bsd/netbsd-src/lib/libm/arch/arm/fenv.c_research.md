# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/fenv.c

ARM VFP floating-point environment implementation. It manipulates `FPSCR` cumulative exception, enable, and rounding-mode fields through `armreg_fpscr_read/write`.

Implements the full fenv API plus `feenableexcept`, `fedisableexcept`, and `fegetexcept`.
