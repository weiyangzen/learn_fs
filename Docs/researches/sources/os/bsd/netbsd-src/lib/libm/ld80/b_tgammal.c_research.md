# File Research: sources/os/bsd/netbsd-src/lib/libm/ld80/b_tgammal.c

This file implements a full ld80 `tgammal(long double x)`.

It includes `b_logl.c` and `b_expl.c` for split-precision log and exp helpers. For `x >= 6`, it uses a Stirling approximation in `large_gam()`. For moderate positive inputs, it reduces via `G(x+1)=xG(x)` into a rational approximation around the gamma minimum. For small positive inputs it uses `smaller_gam()` to avoid cancellation near zero.

Negative non-integers use the reflection formula through `neg_gam()`, calling `sinpil()` or `cospil()` and handling extreme negative values via `lgammal()` and `expl()`. Negative integers return NaN.

The public `tgammal()` handles overflow above `xmax`, reciprocal behavior near zero, non-finite inputs, and signs for reflected values.
