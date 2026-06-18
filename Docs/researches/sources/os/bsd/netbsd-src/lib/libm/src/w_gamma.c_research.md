# File Research: sources/os/bsd/netbsd-src/lib/libm/src/w_gamma.c

Implements legacy double `gamma(x)` as the logarithmic gamma function through `__ieee754_lgamma_r(x, &signgam)`. In non-IEEE modes, nonfinite results from finite inputs are reported as either pole or overflow.

Important dependencies: `math.h`, `math_private.h`, `signgam`, `floor()`, `finite()`, and `__kernel_standard`.

Error codes: `41` for nonpositive integer poles and `40` for overflow.
