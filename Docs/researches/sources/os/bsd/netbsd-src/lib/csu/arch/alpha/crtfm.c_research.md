# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtfm.c

Alpha-specific support for GCC `-ffast-math`. It provides a statically linkable `__alpha_sysarch` syscall wrapper and a constructor that sets floating-point control state.

The constructor calls `ALPHA_SET_FP_C` with `IEEE_MAP_DMZ|IEEE_MAP_UMZ`, enabling denormal/underflow mapping behavior expected by fast-math code.
