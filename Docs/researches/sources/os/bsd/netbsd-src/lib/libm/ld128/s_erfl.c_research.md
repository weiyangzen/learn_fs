# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/s_erfl.c

This file implements `erfl(long double x)` and `erfcl(long double x)`.

It is an ld128 adaptation of Sun fdlibm `erf`/`erfc`, with separate rational approximations by input range. Small values use a power-series style approximation; values around 1 use a correction around `erx`; medium and large values use rational approximations for the logarithmic erfc tail and exponentials.

`erfl()` saturates to `+/-1` for sufficiently large magnitude, using volatile `tiny` to raise or avoid expected exceptions. `erfcl()` handles negative large values returning nearly `2`, positive large values underflowing toward `0`, and NaN/Inf cases explicitly.

The implementation depends on `expl`, bit extraction macros, and many coefficient blocks tuned for ld128 accuracy.
