# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_asinh.c

This file implements public double `asinh(double x)`.

It uses the identity `asinh(x) = sign(x)*log(|x| + sqrt(x*x+1))` with range-specific stable forms: tiny inputs return `x`, very large inputs use `log(|x|)+ln2`, medium-large inputs use `log(2|x| + 1/(sqrt(x*x+1)+|x|))`, and smaller normal inputs use `log1p(|x| + x*x/(1+sqrt(1+x*x)))`.

Dependencies include `__ieee754_log`, `__ieee754_sqrt`, `log1p`, `fabs`, and double high-word macros.
