# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.fenv.inc

This makefile fragment adds floating-environment support files for the libc softfloat build.

It extends `.PATH` to `${.CURDIR}/softfloat`, adds architecture and shared softfloat include directories, defines `SOFTFLOAT_FOR_GCC`, and appends the floating environment accessors to `SRCS`: `fpgetround.c`, `fpsetround.c`, `fpgetmask.c`, `fpsetmask.c`, `fpgetsticky.c`, and `fpsetsticky.c`.

Research notes and risks:
- Defining `SOFTFLOAT_FOR_GCC` narrows softfloat compilation to the ABI/compiler-support subset expected by this libc build.
- The fragment is included by `Makefile.inc`, so changes here affect all softfloat build variants using that include.
