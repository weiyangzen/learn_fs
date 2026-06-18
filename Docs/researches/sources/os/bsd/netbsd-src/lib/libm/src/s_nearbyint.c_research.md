# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nearbyint.c

Implements `nearbyint()`, `nearbyintf()`, and `nearbyintl()` with a macro template.

Key behavior: saves the floating-point environment, calls the corresponding `rint` function, restores the environment with `fesetenv()`, and therefore avoids raising inexact.

Important dependencies: `fenv.h`, `math.h`, and `rint`/`rintf`/`rintl`.

Notable risks: assumes rounding cannot overflow for supported formats.
