# File Research: sources/os/bsd/netbsd-src/lib/libm/src/namespace.h

This header remaps many public libm and fenv symbol names to underscored internal names during libm builds.

It covers elementary real functions, complex inverse trig functions, long-double variants, `fenv` functions, `finite`, `remquo`, scaling functions, `sincos`, pi-multiple trig functions, and gamma functions. This allows implementation files to call internal symbols and avoid namespace or interposition issues.

The file is purely preprocessor definitions and contains no executable code.
