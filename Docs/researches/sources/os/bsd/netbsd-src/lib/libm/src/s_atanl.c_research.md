# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_atanl.c

This file implements public long-double `atanl(long double x)` when long double exists.

It includes ld80 or ld128 inverse-trig constants/helpers from `invtrig.h`, inspects exponent and significand bits to classify ranges, reduces to intervals around `0`, `0.5`, `1`, `1.5`, or infinity, evaluates long-double polynomial helpers `T_even()` and `T_odd()`, and adds split `atanhi`/`atanlo` constants. Large finite inputs return signed `pi/2`, NaNs propagate, and tiny inputs return `x`.

Dependencies include `namespace.h`, machine IEEE layout, `math_private.h`, and the selected long-double inverse-trig header.
